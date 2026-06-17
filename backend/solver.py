"""
solver.py — Generator jadwal otomatis menggunakan Google OR-Tools CP-SAT Solver
Blueprint: SYSTEM_BLUEPRINT.md §5, §6
Schema: class_subjects tanpa id_guru; timetable via id_class_subject.
Guru dipilih dari pool teacher_subjects (pool-based, bukan fixed-guru).
"""
import json
import logging
from ortools.sat.python import cp_model
from backend.database import get_db_connection, db_fetchall
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Konstanta Grid (Blueprint §3)
# ─────────────────────────────────────────────

DAYS_ORDER   = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]

SHIFT_LIMITS = {
    "PAGI":  {"SENIN": 7, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 7},
    "SIANG": {"SENIN": 7, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 6},
}


# ─────────────────────────────────────────────
# Helpers kategori mapel
# ─────────────────────────────────────────────

def _is_olahraga(nama_mapel: str, kategori_mapel: str) -> bool:
    s = (nama_mapel or "").upper()
    k = (kategori_mapel or "").upper()
    return any(kw in s for kw in ("JASMANI", "OLAH RAGA", "PENJASORKES", "OLAHRAGA", "PJOK")) \
        or "OLAHRAGA" in k


def _is_produktif(nama_mapel: str, kategori_mapel: str) -> bool:
    if _is_olahraga(nama_mapel, kategori_mapel):
        return False
    GENERAL = [
        "AGAMA", "PANCASILA", "PPKN", "KEWARGANEGARAAN", "BAHASA INDONESIA",
        "MATEMATIKA", "SEJARAH", "BAHASA INGGRIS", "SENI BUDAYA",
        "INFORMATIKA", "IPAS",
    ]
    s = (nama_mapel or "").upper()
    return not any(g in s for g in GENERAL)


# ─────────────────────────────────────────────
# Wall-clock mapping (Blueprint §3)
# ─────────────────────────────────────────────

def _slot_time(day: str, shift: str, jp: int):
    if shift == "PAGI":
        if day == "JUMAT":
            slots = [(420,460),(460,500),(500,540),(540,580),(600,640),(640,680)]
        elif day == "SENIN":
            # JP 1: 06:30-07:30 (Upacara), JP 2: 07:30-08:10, JP 3: 08:10-08:50, JP 4: 08:50-09:30,
            # JP 5: 10:00-10:35, JP 6: 10:35-11:10, JP 7: 11:10-11:45
            slots = [(390,450),(450,490),(490,530),(530,570),(600,635),(635,670),(670,705)]
        else:
            slots = [(420,465),(465,510),(510,555),(555,600),(630,675),(675,720),(720,765)]
    else:  # SIANG
        if day == "JUMAT":
            slots = [(780,820),(820,860),(860,900),(900,940),(960,1000),(1000,1040)]
        elif day == "SABTU":
            slots = [(765,810),(810,855),(855,900),(900,945),(975,1020),(1020,1065)]
        else:
            slots = [(765,810),(810,855),(855,900),(900,945),(975,1020),(1020,1065),(1065,1110)]
    if 1 <= jp <= len(slots):
        return slots[jp - 1]
    return (0, 0)


# ─────────────────────────────────────────────
# Fetch data dari Supabase
# ─────────────────────────────────────────────

def _fetch_master_data():
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT * FROM teachers ORDER BY id_guru")
        for t in teachers:
            t["hari_tersedia"]       = json.loads(t["hari_tersedia"] or "[]") or []
            t["shift_pagi"]          = bool(t["shift_pagi"])
            t["shift_siang"]         = bool(t["shift_siang"])
            t["hari_tersedia_pagi"]  = (json.loads(t["hari_tersedia_pagi"]) if t.get("hari_tersedia_pagi") else None) or list(t["hari_tersedia"])
            t["hari_tersedia_siang"] = (json.loads(t["hari_tersedia_siang"]) if t.get("hari_tersedia_siang") else None) or list(t["hari_tersedia"])
            t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"]) if t.get("allowed_jp_pagi") else None
            t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"]) if t.get("allowed_jp_siang") else None

        classes = db_fetchall(conn, "SELECT * FROM classes ORDER BY id_kelas")

        subjects_map = {
            s["id_mapel"]: s
            for s in db_fetchall(conn, "SELECT * FROM subjects ORDER BY id_mapel")
        }

        # Alokasi: class_subjects dengan id_guru_mutlak
        allocations = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
                   c.nama_kelas, c.shift_operasional,
                   s.nama_mapel, s.kategori_mapel
            FROM   class_subjects cs
            JOIN   classes  c ON cs.id_kelas = c.id_kelas
            JOIN   subjects s ON cs.id_mapel  = s.id_mapel
        """)

        # Pool kualifikasi guru per mapel: set of (id_guru, id_mapel)
        ts_rows = db_fetchall(conn, "SELECT id_guru, id_mapel FROM teacher_subjects")
        ts_set: set = {(r["id_guru"], r["id_mapel"]) for r in ts_rows}

    finally:
        conn.close()
    return teachers, classes, subjects_map, allocations, ts_set


# ─────────────────────────────────────────────
# Pre-flight checks (Blueprint §6 Tahap 1)
# ─────────────────────────────────────────────

def _preflight(teachers, classes, allocations, ts_set, subjects_map=None):
    errors   = []
    warnings = []

    teachers_map = {t["id_guru"]: t for t in teachers}

    # 1. Total JP per kelas ≤ 40
    class_jp: dict = {}
    for a in allocations:
        class_jp[a["id_kelas"]] = class_jp.get(a["id_kelas"], 0) + a["durasi_jp"]
    for kelas_id, jp in class_jp.items():
        kelas_nama = next((c["nama_kelas"] for c in classes if c["id_kelas"] == kelas_id), str(kelas_id))
        if jp > 40:
            errors.append(f"Kelas [{kelas_nama}] total JP [{jp}] melebihi batas 40 JP!")
        elif jp < 40:
            warnings.append(f"Kelas [{kelas_nama}] total JP [{jp}] < 40 JP. Sisa slot diisi KOSONG.")

    # 2. Olahraga wajib tepat 2 JP
    for a in allocations:
        if _is_olahraga(a["nama_mapel"], a["kategori_mapel"]) and a["durasi_jp"] != 2:
            errors.append(
                f"Kelas [{a['nama_kelas']}] Mapel OLAHRAGA [{a['nama_mapel']}] "
                f"harus tepat 2 JP (ditemukan {a['durasi_jp']} JP). Hard Constraint."
            )

    # 3. Setiap alokasi harus punya ≥1 guru kualifikasi di shift yang sesuai
    for a in allocations:
        shift = a["shift_operasional"]
        id_fixed = a.get("id_guru_mutlak")
        
        if id_fixed:
            # Jika ada guru mutlak, cek hanya ketersediaan guru tersebut
            t = teachers_map.get(id_fixed)
            if not t:
                errors.append(f"Guru Mutlak ID {id_fixed} untuk [{a['nama_mapel']}] di Kelas [{a['nama_kelas']}] tidak ditemukan.")
                continue
            
            if not ((shift == "PAGI" and t["shift_pagi"]) or (shift == "SIANG" and t["shift_siang"])):
                errors.append(f"Guru Mutlak [{t['nama_guru']}] tidak tersedia untuk shift {shift} (Kelas {a['nama_kelas']}).")
            
            # Cek ketersediaan hari (opsional: minimal punya 1 hari tersedia)
            avail = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
            if not avail:
                errors.append(f"Guru Mutlak [{t['nama_guru']}] tidak memiliki ketersediaan hari di shift {shift}.")
        else:
            # Logika regular
            qualified = [
                gid for (gid, mid) in ts_set
                if mid == a["id_mapel"]
                and teachers_map.get(gid)
                and (
                    (shift == "PAGI"  and teachers_map[gid]["shift_pagi"])  or
                    (shift == "SIANG" and teachers_map[gid]["shift_siang"])
                )
            ]
            if not qualified:
                errors.append(
                    f"Tidak ada guru yang kualifikasi untuk [{a['nama_mapel']}] "
                    f"di Kelas [{a['nama_kelas']}] (shift {shift}). "
                    f"Tambahkan penugasan guru di Tab 5."
                )

    # 4. Guru Mutlak (Fixed Teacher) Capacity / Availability Check
    locked_allocs = {}
    for a in allocations:
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed:
            shift = a["shift_operasional"]
            locked_allocs.setdefault((id_fixed, shift), []).append(a)
            
    for (tid, shift), allocs in locked_allocs.items():
        t = teachers_map.get(tid)
        if not t:
            continue
        locked_jp = sum(a["durasi_jp"] for a in allocs)
        avail_days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
        
        max_slots = 0
        for d in avail_days:
            allowed_jp = t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
            if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
            else:
                max_jp = SHIFT_LIMITS[shift].get(d, 0)
                day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
            max_slots += day_slots
        
        if locked_jp > max_slots:
            errors.append(
                f"Guru Mutlak [{t['nama_guru']}] dikunci untuk total {locked_jp} JP pada shift {shift}, "
                f"tetapi hari ketersediaannya ({', '.join(avail_days)}) hanya menampung maksimal {max_slots} JP."
            )

    # 5. Shift Capacity & Availability check for each Subject
    if subjects_map:
        subj_shift_allocs = {}
        for a in allocations:
            key = (a["id_mapel"], a["shift_operasional"])
            subj_shift_allocs.setdefault(key, []).append(a)
            
        for (mid, shift), allocs in subj_shift_allocs.items():
            subj_name = subjects_map.get(mid, {}).get("nama_mapel", f"ID {mid}")
            total_demand = sum(a["durasi_jp"] for a in allocs)
            
            # Who are the qualified teachers for this mapel in this shift?
            qualified = []
            for t in teachers:
                tid = t["id_guru"]
                if (tid, mid) in ts_set:
                    if (shift == "PAGI" and t["shift_pagi"]) or (shift == "SIANG" and t["shift_siang"]):
                        qualified.append(t)
                        
            if not qualified:
                continue
                
            total_max_capacity = sum(t["max_jp"] if t["max_jp"] is not None else 60 for t in qualified)
            if total_demand > total_max_capacity:
                errors.append(
                    f"Mapel [{subj_name}] di shift {shift} membutuhkan total {total_demand} JP, "
                    f"tetapi total kapasitas mengajar guru yang kualifikasi hanya {total_max_capacity} JP."
                )
                
            # Availability slots check
            union_days = set()
            for t in qualified:
                days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                union_days.update(days)
                
            if not union_days:
                errors.append(
                    f"Guru pengampu kualifikasi untuk Mapel [{subj_name}] di shift {shift} "
                    f"tidak memiliki hari ketersediaan."
                )
                continue
                
            if len(qualified) == 1:
                single_t = qualified[0]
                max_daily_slots = 0
                for d in union_days:
                    allowed_jp = single_t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
                    if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                        day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                    else:
                        max_jp = SHIFT_LIMITS[shift].get(d, 0)
                        day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                    max_daily_slots += day_slots
                    
                if total_demand > max_daily_slots:
                    errors.append(
                        f"Mapel [{subj_name}] di shift {shift} membutuhkan {total_demand} JP, "
                        f"namun satu-satunya guru kualifikasi ({single_t['nama_guru']}) hanya tersedia "
                        f"hari {', '.join(union_days)} dengan kapasitas maksimal {max_daily_slots} JP."
                    )
            else:
                combined_slots = 0
                for d in union_days:
                    for t in qualified:
                        if d in (t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]):
                            allowed_jp = t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
                            if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                                day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                            else:
                                max_jp = SHIFT_LIMITS[shift].get(d, 0)
                                day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                            combined_slots += day_slots
                    
                if total_demand > combined_slots:
                    errors.append(
                        f"Mapel [{subj_name}] di shift {shift} membutuhkan total {total_demand} JP, "
                        f"tetapi hari ketersediaan guru pengampu ({', '.join(union_days)}) hanya memiliki "
                        f"kapasitas gabungan maksimal {combined_slots} JP."
                    )

        # 6. Olahraga Field Capacity Check (Maks 1 kelas bersamaan)
        for shift in ["PAGI", "SIANG"]:
            oly_allocs = [
                a for a in allocations 
                if a["shift_operasional"] == shift and _is_olahraga(a["nama_mapel"], a["kategori_mapel"])
            ]
            if oly_allocs:
                oly_demand = sum(a["durasi_jp"] for a in oly_allocs)
                max_oly_slots = sum(SHIFT_LIMITS[shift].get(d, 0) for d in DAYS_ORDER)
                if oly_demand > max_oly_slots:
                    errors.append(
                        f"Total JP Olahraga pada shift {shift} adalah {oly_demand} JP, tetapi lapangan "
                        f"hanya dapat digunakan maksimal {max_oly_slots} JP per minggu (Maks 1 kelas bersamaan)."
                    )

    # 7. Teacher Total Max JP vs Locked JP Check
    teacher_locked_totals = {}
    for a in allocations:
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed:
            teacher_locked_totals[id_fixed] = teacher_locked_totals.get(id_fixed, 0) + a["durasi_jp"]
            
    for tid, locked_tot in teacher_locked_totals.items():
        t = teachers_map.get(tid)
        if t and t["max_jp"] is not None and locked_tot > t["max_jp"]:
            errors.append(
                f"Guru Mutlak [{t['nama_guru']}] dikunci untuk total {locked_tot} JP secara keseluruhan, "
                f"tetapi batasan jam mengajar maksimalnya (Max JP) disetel hanya {t['max_jp']} JP."
            )

    # 8. Daily Coverage Feasibility Check (Mathematical Blocker)
    for shift in ["PAGI", "SIANG"]:
        shift_classes = [c for c in classes if c["shift_operasional"] == shift]
        n_kelas = len(shift_classes)
        if n_kelas == 0:
            continue
            
        # Calculate maximum empty slots in the week for this shift
        total_grid_slots = sum(SHIFT_LIMITS[shift].values())
        
        # Calculate allocated JP per class in this shift
        class_ids = {c["id_kelas"] for c in shift_classes}
        allocated_jp = {}
        for a in allocations:
            if a["id_kelas"] in class_ids:
                allocated_jp[a["id_kelas"]] = allocated_jp.get(a["id_kelas"], 0) + a["durasi_jp"]
                
        max_empty_slots = sum(max(0, total_grid_slots - allocated_jp.get(cid, 0)) for cid in class_ids)
        
        # Calculate minimum empty slots required by teacher shortage
        min_empty_required = 0
        shortage_days = []
        for day in DAYS_ORDER:
            # Count teachers available on this day and shift
            n_guru = sum(
                1 for t in teachers
                if (shift == "PAGI" and t["shift_pagi"] and day in t["hari_tersedia_pagi"])
                or (shift == "SIANG" and t["shift_siang"] and day in t["hari_tersedia_siang"])
            )
            if n_guru < n_kelas:
                shortage = n_kelas - n_guru
                day_slots = SHIFT_LIMITS[shift].get(day, 0)
                min_empty_required += day_slots * shortage
                shortage_days.append(f"{day} (kurang {shortage} guru)")
                
        if min_empty_required > max_empty_slots:
            errors.append(
                f"Ketersediaan guru pada shift {shift} tidak layak secara matematis! "
                f"Kekurangan guru pada hari {', '.join(shortage_days)} mengharuskan setidaknya "
                f"{min_empty_required} slot kosong secara kumulatif, tetapi alokasi JP kelas hanya menyisakan "
                f"maksimal {max_empty_slots} slot kosong di grid."
            )

    # 9. Sole Qualified Teacher Load Check
    alloc_candidates = {}
    for a in allocations:
        shift = a["shift_operasional"]
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed:
            alloc_candidates[a["id_class_subject"]] = {id_fixed}
        else:
            cands = {
                t["id_guru"] for t in teachers
                if (t["id_guru"], a["id_mapel"]) in ts_set
                and (
                    (shift == "PAGI" and t["shift_pagi"])
                    or (shift == "SIANG" and t["shift_siang"])
                )
            }
            alloc_candidates[a["id_class_subject"]] = cands

    sole_demand = {}
    for a in allocations:
        cands = alloc_candidates.get(a["id_class_subject"], set())
        if len(cands) == 1:
            tid = list(cands)[0]
            sole_demand.setdefault(tid, []).append(a)

    for tid, allocs_for_teacher in sole_demand.items():
        t = teachers_map.get(tid)
        if not t:
            continue
        total_sole_jp = sum(a["durasi_jp"] for a in allocs_for_teacher)
        
        # Check overall max_jp
        if t["max_jp"] is not None and total_sole_jp > t["max_jp"]:
            errors.append(
                f"Guru [{t['nama_guru']}] adalah satu-satunya pengampu untuk beberapa mapel "
                f"dengan total {total_sole_jp} JP, tetapi batas mengajar maksimalnya disetel hanya {t['max_jp']} JP."
            )

        # Check shift-specific slots
        for shift in ["PAGI", "SIANG"]:
            shift_allocs = [a for a in allocs_for_teacher if a["shift_operasional"] == shift]
            shift_jp = sum(a["durasi_jp"] for a in shift_allocs)
            if shift_jp > 0:
                avail_days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                max_slots = 0
                for d in avail_days:
                    allowed_jp = t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
                    if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                        day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                    else:
                        max_jp = SHIFT_LIMITS[shift].get(d, 0)
                        day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                    max_slots += day_slots
                
                if shift_jp > max_slots:
                    errors.append(
                        f"Guru [{t['nama_guru']}] adalah satu-satunya pengampu pada shift {shift} "
                        f"untuk total {shift_jp} JP, tetapi ketersediaan harinya hanya menampung maksimal {max_slots} JP."
                    )

    # 10. Shared Candidate Groups Capacity Check
    candidate_groups = {}
    for a in allocations:
        cands = tuple(sorted(alloc_candidates.get(a["id_class_subject"], set())))
        if cands:
            candidate_groups.setdefault(cands, []).append(a)

    for cands_tuple, allocs_for_group in candidate_groups.items():
        if len(cands_tuple) > 4:
            continue
        total_group_demand = sum(a["durasi_jp"] for a in allocs_for_group)
        combined_max_jp = sum(teachers_map[tid]["max_jp"] if teachers_map[tid]["max_jp"] is not None else 60 for tid in cands_tuple)
        if total_group_demand > combined_max_jp:
            names = [teachers_map[tid]["nama_guru"] for tid in cands_tuple]
            errors.append(
                f"Kelompok guru {names} mengampu beberapa mapel dengan total kebutuhan {total_group_demand} JP, "
                f"tetapi gabungan kapasitas mengajar maksimal mereka hanya {combined_max_jp} JP."
            )

    # 11. Olahraga Teacher Availability Check
    for shift in ["PAGI", "SIANG"]:
        oly_allocs = [
            a for a in allocations 
            if a["shift_operasional"] == shift and _is_olahraga(a["nama_mapel"], a["kategori_mapel"])
        ]
        if not oly_allocs:
            continue
            
        oly_teacher_ids = set()
        for a in oly_allocs:
            oly_teacher_ids.update(alloc_candidates.get(a["id_class_subject"], set()))
            
        if not oly_teacher_ids:
            continue
            
        n_oly_classes = len(oly_allocs)
        day_capacities = {}
        for tid in oly_teacher_ids:
            t = teachers_map.get(tid)
            avail_days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
            for d in avail_days:
                day_capacities[d] = 3
                
        total_oly_slots_available = sum(day_capacities.values())
        if n_oly_classes > total_oly_slots_available:
            names = [teachers_map[tid]["nama_guru"] for tid in oly_teacher_ids]
            errors.append(
                f"Total {n_oly_classes} kelas Olahraga di shift {shift} tidak dapat dijadwalkan! "
                f"Guru Olahraga yang tersedia ({', '.join(names)}) hanya aktif pada hari "
                f"{', '.join(day_capacities.keys())} yang hanya dapat menampung maksimal {total_oly_slots_available} kelas."
            )

    return errors, warnings


# ─────────────────────────────────────────────
# Sorting antrean kritis (Blueprint §6 Tahap 2)
# ─────────────────────────────────────────────

def _sort_allocations(allocations, ts_set):
    """
    Prioritas:
    1. OLAHRAGA (blok constraint ketat)
    2. Mapel dengan pool guru paling sedikit (most constrained)
    3. PRODUKTIF durasi panjang (≥4 JP)
    4. Sisanya
    """
    def _pool_size(a):
        return sum(1 for (_, mid) in ts_set if mid == a["id_mapel"])

    def priority(a):
        if _is_olahraga(a["nama_mapel"], a["kategori_mapel"]):
            return (1, 0)
        pool = _pool_size(a)
        if pool <= 1:
            return (2, pool)
        if _is_produktif(a["nama_mapel"], a["kategori_mapel"]) and a["durasi_jp"] >= 4:
            return (3, -a["durasi_jp"])
        return (4, 0)

    return sorted(allocations, key=priority)


# ─────────────────────────────────────────────
# Core Solver (Blueprint §6 Tahap 3)
# ─────────────────────────────────────────────

# Stage mode: mengontrol pool guru yang diizinkan
STAGE_FULL_QUAL    = "FULL_QUAL"     # hanya guru dengan kualifikasi mapel tepat
STAGE_CAT_QUAL     = "CAT_QUAL"      # guru dengan kualifikasi kategori mapel sama
STAGE_SHIFT_ONLY   = "SHIFT_ONLY"    # semua guru yang shift-nya sesuai (tanpa kualifikasi)


active_solver = None
active_stage = 0
abort_requested = False

def interrupt_active_solver():
    global active_solver, abort_requested
    abort_requested = True
    if active_solver:
        active_solver.stop_search()
        return True
    return False

def _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, stage):
    """
    Membangun daftar kandidat guru per alokasi sesuai mode stage.
    """
    candidates = {}
    for a in allocations:
        shift    = classes_map[a["id_kelas"]]["shift_operasional"]
        id_mapel = a["id_mapel"]
        id_fixed = a.get("id_guru_mutlak")
        subj     = subjects_map.get(id_mapel, {})
        cat      = (subj.get("kategori_mapel") or "").upper()
        cands    = []

        # JIKA ADA GURU MUTLAK: langsung batasi kandidat ke guru tersebut saja
        if id_fixed:
            # Pastikan guru mutlak ini ada di daftar teachers (seharusnya selalu ada)
            # Pencocokan dilakukan menggunakan ID (Integer), bukan Nama.
            fixed_exists = any(t["id_guru"] == id_fixed for t in teachers)
            if fixed_exists:
                candidates[a["id_class_subject"]] = [id_fixed]
                continue
            else:
                logger.warning(f"Alokasi ID {a['id_class_subject']} (Mapel {a['nama_mapel']} di Kelas {a['nama_kelas']}) menetapkan Guru Mutlak ID {id_fixed} tapi ID guru tersebut tidak ditemukan di database.")
                # Lanjut ke logika regular jika ID guru mutlak tidak valid (fallback)

        for t in teachers:
            tid = t["id_guru"]

            # Filter shift
            if not ((shift == "PAGI" and t["shift_pagi"]) or
                    (shift == "SIANG" and t["shift_siang"])):
                continue

            if stage == STAGE_FULL_QUAL:
                # Hanya guru yang punya kualifikasi persis mapel ini
                if not ts_set or (tid, id_mapel) not in ts_set:
                    continue

            elif stage == STAGE_CAT_QUAL:
                # Guru yang punya kualifikasi di mapel dengan kategori sama
                same_cat_mapels = {
                    mid for (gid, mid) in ts_set
                    if gid == tid
                    and (subjects_map.get(mid, {}).get("kategori_mapel") or "").upper() == cat
                }
                if not same_cat_mapels:
                    continue

            # STAGE_SHIFT_ONLY: tidak ada filter tambahan

            cands.append(tid)

        candidates[a["id_class_subject"]] = cands
    return candidates


def _run_solver(teachers, classes, allocations, ts_set, subjects_map, stage, time_limit=30.0):
    """
    Menjalankan CP-SAT solver untuk stage tertentu.
    Return dict hasil atau None jika infeasible.
    """
    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    allocations_map = {a["id_class_subject"]: a for a in allocations}

    candidates = _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, stage)

    # ── Buat variabel keputusan ───────────────────────────────────────
    model = cp_model.CpModel()
    x: dict = {}

    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        c_allocs = [a for a in allocations if a["id_kelas"] == cid]

        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for jp in range(1, max_jp + 1):
                # UPACARA BENDERA: Senin JP 1 Pagi tidak boleh ada pelajaran
                if day == "SENIN" and jp == 1 and shift == "PAGI":
                    continue

                for a in c_allocs:
                    aid = a["id_class_subject"]
                    for tid in candidates.get(aid, []):
                        t   = teachers_map[tid]
                        avail = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                        if day in avail:
                            allowed_jp = t["allowed_jp_pagi"] if shift == "PAGI" else t["allowed_jp_siang"]
                            if allowed_jp and isinstance(allowed_jp, dict):
                                allowed_jps_for_day = allowed_jp.get(day) or allowed_jp.get(day.upper()) or allowed_jp.get(day.lower())
                                if allowed_jps_for_day is not None:
                                    if jp not in allowed_jps_for_day:
                                        continue

                            key = (cid, day, jp, aid, tid)
                            x[key] = model.NewBoolVar(
                                f"x_c{cid}_{day}_jp{jp}_a{aid}_t{tid}"
                            )

    # ── Lookup cepat ─────────────────────────────────────────────────
    by_class_slot:  dict = {}
    by_alloc_slot:  dict = {}
    by_alloc:       dict = {}
    by_alloc_day:   dict = {}
    by_teacher_day: dict = {}
    by_aid_tid:     dict = {}  # Baru: untuk constraint 1 guru per alokasi

    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp),       []).append(var)
        by_alloc_slot.setdefault((cid, day, jp, aid),  []).append(var)
        by_alloc.setdefault((cid, aid),                []).append(var)
        by_alloc_day.setdefault((cid, aid, day),       []).append(var)
        by_teacher_day.setdefault((tid, day),          []).append(key)
        by_aid_tid.setdefault((aid, tid),              []).append(var)

    # ── Constraint 1: Maks 1 pelajaran per slot kelas ────────────────
    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                vs = by_class_slot.get((cid, day, jp), [])
                if vs:
                    model.Add(sum(vs) <= 1)

    # ── Constraint 2: Terpenuhi durasi JP per alokasi ─────────────────
    for a in allocations:
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        vs  = by_alloc.get((cid, aid), [])
        if vs:
            model.Add(sum(vs) == a["durasi_jp"])
        elif a["durasi_jp"] > 0:
            logger.warning(f"Alokasi [{aid}] tidak ada kandidat — infeasible untuk stage ini.")
            return None

    # ── Constraint 2b: 1 Kelas + 1 Mapel = hanya 1 Guru (HARD CONSTRAINT) ────
    # Untuk setiap alokasi (kelas+mapel), semua slot WAJIB diajarkan oleh
    # guru yang SAMA. Tidak boleh satu mapel dibagi ke beberapa guru.
    for a in allocations:
        aid = a["id_class_subject"]
        cands = candidates.get(aid, [])
        if not cands:
            continue

        # g[tid] = 1 jika guru tid dipilih untuk alokasi aid
        g_vars = {}
        for tid in cands:
            gv = model.NewBoolVar(f"g_a{aid}_t{tid}")
            g_vars[tid] = gv
            
            # Semua slot untuk (aid, tid) hanya boleh aktif jika gv aktif
            for var in by_aid_tid.get((aid, tid), []):
                model.Add(var <= gv)

        # Tepat 1 guru yang dipilih untuk alokasi ini (jika ada JP > 0)
        if a["durasi_jp"] > 0:
            model.Add(sum(g_vars.values()) == 1)
        else:
            # Jika durasi 0, tidak perlu ada guru
            model.Add(sum(g_vars.values()) == 0)

    # ── Constraint 3: No Teacher Clash (wall-clock) ──────────────────
    for day in DAYS_ORDER:
        tid_keys: dict = {}
        for c in classes:
            cid   = c["id_kelas"]
            shift = c["shift_operasional"]
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                for a in [al for al in allocations if al["id_kelas"] == cid]:
                    for tid in candidates.get(a["id_class_subject"], []):
                        key = (cid, day, jp, a["id_class_subject"], tid)
                        if key in x:
                            tid_keys.setdefault(tid, []).append(key)

        time_pts: set = set()
        for keys in tid_keys.values():
            for key in keys:
                cid2, _, jp2, _, _ = key
                s, e = _slot_time(day, classes_map[cid2]["shift_operasional"], jp2)
                if s < e:
                    time_pts.add(s); time_pts.add(e)

        sorted_pts = sorted(time_pts)
        for t0, t1 in zip(sorted_pts, sorted_pts[1:]):
            for tid, keys in tid_keys.items():
                overlap_vars = []
                for key in keys:
                    cid2, _, jp2, _, _ = key
                    s, e = _slot_time(day, classes_map[cid2]["shift_operasional"], jp2)
                    if s < t1 and e > t0:
                        overlap_vars.append(x[key])
                if len(overlap_vars) > 1:
                    model.Add(sum(overlap_vars) <= 1)

    # ── Constraint 4: Olahraga — blok 2 JP berturut ──────────────────
    for a in allocations:
        if not _is_olahraga(a["nama_mapel"], a["kategori_mapel"]):
            continue
        cid   = a["id_kelas"]
        aid   = a["id_class_subject"]
        shift = classes_map[cid]["shift_operasional"]

        y_blocks: dict = {}
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for start in [1, 2, 3, 5] + ([6] if max_jp >= 7 else []):
                if start + 1 > max_jp:
                    continue
                if (by_alloc_slot.get((cid, day, start, aid)) and
                        by_alloc_slot.get((cid, day, start + 1, aid))):
                    yv = model.NewBoolVar(f"y_c{cid}_a{aid}_{day}_s{start}")
                    y_blocks[(day, start)] = yv

        if not y_blocks:
            logger.error(f"Tidak ada slot blok valid untuk Olahraga [{a['nama_kelas']}].")
            return None

        model.Add(sum(y_blocks.values()) == 1)

        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for jp in range(1, max_jp + 1):
                covering = []
                if (day, jp)     in y_blocks: covering.append(y_blocks[(day, jp)])
                if (day, jp - 1) in y_blocks: covering.append(y_blocks[(day, jp - 1)])
                slot_vars = by_alloc_slot.get((cid, day, jp, aid), [])
                if slot_vars:
                    if covering:
                        model.Add(sum(slot_vars) == sum(covering))
                    else:
                        model.Add(sum(slot_vars) == 0)

    # ── Constraint 5: Kapasitas Lapangan Olahraga (Maks 1 Kelas Bersamaan) ──
    olahraga_keys = []
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        a = allocations_map.get(aid)
        if a and _is_olahraga(a["nama_mapel"], a["kategori_mapel"]):
            olahraga_keys.append(key)

    for day in DAYS_ORDER:
        time_pts = set()
        day_oly_keys = [k for k in olahraga_keys if k[1] == day]
        for key in day_oly_keys:
            cid, _, jp, _, _ = key
            s, e = _slot_time(day, classes_map[cid]["shift_operasional"], jp)
            if s < e:
                time_pts.add(s)
                time_pts.add(e)
                
        sorted_pts = sorted(time_pts)
        for t0, t1 in zip(sorted_pts, sorted_pts[1:]):
            overlap_vars = []
            for key in day_oly_keys:
                cid, _, jp, _, _ = key
                s, e = _slot_time(day, classes_map[cid]["shift_operasional"], jp)
                if s < t1 and e > t0:
                    overlap_vars.append(x[key])
            if len(overlap_vars) > 1:
                model.Add(sum(overlap_vars) <= 1)

    # ── Soft Constraint: Preferensi jam berurutan per alokasi (jika durasi_jp > 1)
    # Tujuan: Mendorong agar jam mengajar untuk mapel yang sama pada hari yang sama
    # ditempatkan secara berurutan (tanpa jeda/gap). Menggunakan sistem reward adjacent pairs.
    obj: list = []
    for a in allocations:
        durasi = a["durasi_jp"]
        if durasi <= 1:
            continue

        cid   = a["id_kelas"]
        aid   = a["id_class_subject"]
        shift = classes_map[cid]["shift_operasional"]

        # Reward sebesar 40 untuk setiap sepasang jam berurutan (misal: JP 1 & JP 2)
        # pada hari yang sama untuk alokasi yang sama.
        reward_adjacent = 40
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for jp in range(1, max_jp):
                # Ambil slot variabel keputusan untuk jam jp dan jp+1
                slot_vars_1 = by_alloc_slot.get((cid, day, jp, aid), [])
                slot_vars_2 = by_alloc_slot.get((cid, day, jp + 1, aid), [])
                
                # Hanya buat variabel jika kedua slot tersebut memungkinkan untuk dijadwalkan
                if slot_vars_1 and slot_vars_2:
                    adj_var = model.NewBoolVar(f"adj_c{cid}_a{aid}_{day}_{jp}")
                    model.Add(sum(slot_vars_1) >= adj_var)
                    model.Add(sum(slot_vars_2) >= adj_var)
                    obj.append(reward_adjacent * adj_var)

    # ── Soft Constraint: Pemerataan beban guru (DILIGHTEN SEVERELY) ─────────
    # Hanya catat beban, tanpa logic perbandingan yang berat
    teacher_load_vars = {}
    for tid in {tid for (_, _, _, _, tid) in x}:
        all_t_vars = [var for key, var in x.items() if key[4] == tid]
        if all_t_vars:
            load = model.NewIntVar(0, 200, f"load_{tid}")
            model.Add(load == cp_model.LinearExpr.Sum(all_t_vars))
            teacher_load_vars[tid] = load

    # ── Constraint: Beban Guru (Flexible: NULL = Bebas) ─────────────────────
    teacher_active_vars = {}
    for tid, load in teacher_load_vars.items():
        t_info = teachers_map[tid]
        min_jp_val = t_info.get("min_jp")
        max_jp_val = t_info.get("max_jp")
        
        is_active = model.NewBoolVar(f"active_{tid}")
        model.Add(load <= 200 * is_active)
        model.Add(load >= is_active)
        teacher_active_vars[tid] = is_active
        
        # 1. Jam Minimal: HARD CONSTRAINT HANYA JIKA min_jp DIISI
        if min_jp_val is not None:
            model.Add(load >= min_jp_val * is_active)
            # Wajib aktif jika min_jp > 10
            if min_jp_val > 10:
                model.Add(is_active == 1)
        
        # 2. Jam Maksimal: HARD CONSTRAINT HANYA JIKA max_jp DIISI
        if max_jp_val is not None:
            model.Add(load <= max_jp_val)
        else:
            model.Add(load <= 200)  # Batas wajar
        
        # Bonus ringkas untuk aktif
        obj.append(50 * is_active) 

    # ── Penalti stage fallback ────────────────────────────────────────
    if stage == STAGE_CAT_QUAL:
        for var in x.values():
            obj.append(-500 * var)   # kecil, hanya untuk tiebreak
    elif stage == STAGE_SHIFT_ONLY:
        for var in x.values():
            obj.append(-2000 * var)

    if obj:
        model.Maximize(cp_model.LinearExpr.Sum(obj))

    # ── Solve ─────────────────────────────────────────────────────────
    global active_solver, abort_requested
    if abort_requested:
        return None
    solver = cp_model.CpSolver()
    active_solver = solver
    
    # Gunakan multi-threading (0 = otomatis deteksi jumlah core CPU) untuk stabilitas dan kecepatan maksimal di Windows
    solver.parameters.num_search_workers = 0
    solver.parameters.max_time_in_seconds = time_limit
    try:
        status = solver.Solve(model)
    finally:
        active_solver = None

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    # ── Kumpulkan hasil ───────────────────────────────────────────────
    results      = []
    warn_logs    = []
    fallback_cnt = 0

    for key, var in x.items():
        if solver.Value(var) != 1:
            continue
        cid, day, jp, aid, tid = key
        is_fallback = stage != STAGE_FULL_QUAL

        if is_fallback:
            fallback_cnt += 1
            t_info = teachers_map[tid]
            a_info = allocations_map[aid]
            warn_logs.append(
                f"[SUBSTITUSI/{stage}] {day} | Kelas {a_info['nama_kelas']} | "
                f"JP ke-{jp} | {a_info['nama_mapel']} → "
                f"{t_info['nama_guru']} (kode {t_info['kode_guru']})"
            )

        results.append({
            "id_class_subject":  aid,
            "hari":              day,
            "jam_ke":            jp,
            "id_guru":           tid,
            "is_fallback":       is_fallback,
            "original_guru_id":  None,
        })

    # Hitung total JP per guru dari hasil solve
    teacher_loads = {t["id_guru"]: 0 for t in teachers}
    for r in results:
        tid = r["id_guru"]
        if tid in teacher_loads:
            teacher_loads[tid] += 1

    # Cek min_jp / max_jp per guru
    for tid, load in teacher_loads.items():
        t_info = teachers_map[tid]
        min_jp_val = t_info.get("min_jp") if t_info.get("min_jp") is not None else 2
        max_jp_val = t_info.get("max_jp") if t_info.get("max_jp") is not None else 60
        if load == 0:
            warn_logs.append(
                f"[Tidak Mendapat Jam] Guru {t_info['nama_guru']} (kode {t_info['kode_guru']}) "
                f"tidak mendapat jam mengajar sama sekali."
            )
        elif load < min_jp_val:
            warn_logs.append(
                f"[Beban Kurang] Guru {t_info['nama_guru']} (kode {t_info['kode_guru']}) "
                f"hanya mengajar {load} JP, kurang dari minimal {min_jp_val} JP."
            )
        elif load > max_jp_val:
            warn_logs.append(
                f"[Beban Lebih] Guru {t_info['nama_guru']} (kode {t_info['kode_guru']}) "
                f"mengajar {load} JP, melebihi maksimal {max_jp_val} JP."
            )

    total_possible = sum(
        SHIFT_LIMITS[c["shift_operasional"]][day]
        for c in classes
        for day in DAYS_ORDER
    )
    fill_pct = round(len(results) / total_possible * 100, 1) if total_possible else 0.0

    _save_timetable(results)

    return {
        "status":          "SUCCESS",
        "fill_percentage": fill_pct,
        "fallback_count":  fallback_cnt,
        "warnings":        warn_logs,
        "errors":          [],
    }


# ─────────────────────────────────────────────
# Simpan ke Supabase
# ─────────────────────────────────────────────

def _save_timetable(results):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("DELETE FROM timetable")
        execute_values(cur, """
            INSERT INTO timetable
                (id_class_subject, hari, jam_ke, id_guru, is_fallback, original_guru_id)
            VALUES %s
        """, [
            (r["id_class_subject"], r["hari"], r["jam_ke"],
             r["id_guru"], bool(r["is_fallback"]), r["original_guru_id"])
            for r in results
        ])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
# Diagnosa Infeasibility
# ─────────────────────────────────────────────

def _diagnose_infeasibility(teachers, classes, allocations, ts_set, subjects_map):
    errors = []
    
    # 1. Guru Mutlak (Fixed Teacher) Capacity / Availability
    teachers_map = {t["id_guru"]: t for t in teachers}
    
    # Group locked allocations by teacher and shift
    locked_allocs = {}
    for a in allocations:
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed:
            shift = a["shift_operasional"]
            locked_allocs.setdefault((id_fixed, shift), []).append(a)
            
    for (tid, shift), allocs in locked_allocs.items():
        t = teachers_map.get(tid)
        if not t:
            continue
        locked_jp = sum(a["durasi_jp"] for a in allocs)
        avail_days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
        
        max_slots = 0
        for d in avail_days:
            allowed_jp = t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
            if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
            else:
                max_jp = SHIFT_LIMITS[shift].get(d, 0)
                day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
            max_slots += day_slots
        
        if locked_jp > max_slots:
            errors.append(
                f"Guru Mutlak [{t['nama_guru']}] dikunci untuk total {locked_jp} JP pada shift {shift}, "
                f"tetapi hari ketersediaannya ({', '.join(avail_days)}) hanya menampung maksimal {max_slots} JP."
            )
            
    # 2. Shift Capacity & Availability check for each Subject
    # Group allocations by subject & shift
    subj_shift_allocs = {}
    for a in allocations:
        key = (a["id_mapel"], a["shift_operasional"])
        subj_shift_allocs.setdefault(key, []).append(a)
        
    for (mid, shift), allocs in subj_shift_allocs.items():
        subj_name = subjects_map.get(mid, {}).get("nama_mapel", f"ID {mid}")
        total_demand = sum(a["durasi_jp"] for a in allocs)
        
        # Who are the qualified teachers for this mapel in this shift?
        qualified = []
        for t in teachers:
            tid = t["id_guru"]
            if (tid, mid) in ts_set:
                if (shift == "PAGI" and t["shift_pagi"]) or (shift == "SIANG" and t["shift_siang"]):
                    qualified.append(t)
                    
        if not qualified:
            has_unfixed = any(not a.get("id_guru_mutlak") for a in allocs)
            if has_unfixed:
                errors.append(
                    f"Tidak ada guru yang memenuhi syarat (kualifikasi di Tab 5 & aktif shift {shift}) "
                    f"untuk mengajarkan Mapel [{subj_name}] di shift {shift}."
                )
            continue
            
        total_max_capacity = sum(t["max_jp"] if t["max_jp"] is not None else 60 for t in qualified)
        if total_demand > total_max_capacity:
            errors.append(
                f"Mapel [{subj_name}] di shift {shift} membutuhkan total {total_demand} JP, "
                f"tetapi total kapasitas mengajar guru yang kualifikasi hanya {total_max_capacity} JP."
            )
            
        # Availability slots check
        union_days = set()
        for t in qualified:
            days = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
            union_days.update(days)
            
        if not union_days:
            errors.append(
                f"Guru pengampu kualifikasi untuk Mapel [{subj_name}] di shift {shift} "
                f"tidak memiliki hari ketersediaan."
            )
            continue
            
        if len(qualified) == 1:
            single_t = qualified[0]
            max_daily_slots = 0
            for d in union_days:
                allowed_jp = single_t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
                if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                    day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                else:
                    max_jp = SHIFT_LIMITS[shift].get(d, 0)
                    day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                max_daily_slots += day_slots
                
            if total_demand > max_daily_slots:
                errors.append(
                    f"Mapel [{subj_name}] di shift {shift} membutuhkan {total_demand} JP, "
                    f"namun satu-satunya guru kualifikasi ({single_t['nama_guru']}) hanya tersedia "
                    f"hari {', '.join(union_days)} dengan kapasitas maksimal {max_daily_slots} JP."
                )
        else:
            combined_slots = 0
            for d in union_days:
                for t in qualified:
                    if d in (t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]):
                        allowed_jp = t.get("allowed_jp_pagi" if shift == "PAGI" else "allowed_jp_siang")
                        if allowed_jp and isinstance(allowed_jp, dict) and d in allowed_jp:
                            day_slots = sum(1 for jp in allowed_jp[d] if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                        else:
                            max_jp = SHIFT_LIMITS[shift].get(d, 0)
                            day_slots = sum(1 for jp in range(1, max_jp + 1) if not (d == "SENIN" and jp == 1 and shift == "PAGI"))
                        combined_slots += day_slots
                
            if total_demand > combined_slots:
                errors.append(
                    f"Mapel [{subj_name}] di shift {shift} membutuhkan total {total_demand} JP, "
                    f"tetapi hari ketersediaan guru pengampu ({', '.join(union_days)}) hanya memiliki "
                    f"kapasitas gabungan maksimal {combined_slots} JP."
                )

    # 3. Olahraga Field Capacity Check (Maks 1 kelas bersamaan)
    for shift in ["PAGI", "SIANG"]:
        oly_allocs = [
            a for a in allocations 
            if a["shift_operasional"] == shift and _is_olahraga(a["nama_mapel"], a["kategori_mapel"])
        ]
        if oly_allocs:
            oly_demand = sum(a["durasi_jp"] for a in oly_allocs)
            max_oly_slots = sum(SHIFT_LIMITS[shift].get(d, 0) for d in DAYS_ORDER)
            if oly_demand > max_oly_slots:
                errors.append(
                    f"Total JP Olahraga pada shift {shift} adalah {oly_demand} JP, tetapi lapangan "
                    f"hanya dapat digunakan maksimal {max_oly_slots} JP per minggu (Maks 1 kelas bersamaan)."
                )

    return errors


# ─────────────────────────────────────────────
# Entry point utama
# ─────────────────────────────────────────────

def generate_timetable():
    global active_stage, abort_requested
    abort_requested = False
    active_stage = 0

    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()

    if not classes:
        return {"status": "FAILED", "errors": ["Tidak ada data kelas."], "warnings": []}
    if not allocations:
        return {"status": "FAILED", "errors": ["Tidak ada alokasi kurikulum."], "warnings": []}
    if not ts_set:
        return {"status": "FAILED", "errors": ["Penugasan guru (teacher_subjects) kosong. Isi Tab 5 dulu."], "warnings": []}

    allocations = _sort_allocations(allocations, ts_set)

    logger.info(f"Kualifikasi guru-mapel: {len(ts_set)} relasi dari teacher_subjects.")

    # Pre-flight
    errors, warnings = _preflight(teachers, classes, allocations, ts_set, subjects_map)
    if errors:
        return {"status": "FAILED", "errors": errors, "warnings": warnings}

    # Stage 1 — kualifikasi penuh (hanya guru yang terdaftar di teacher_subjects untuk mapel ini)
    logger.info("Stage 1: Solving dengan kualifikasi penuh...")
    active_stage = 1
    res = _run_solver(teachers, classes, allocations, ts_set, subjects_map,
                      stage=STAGE_FULL_QUAL, time_limit=90.0)
    if res:
        active_stage = 0
        res["warnings"] = warnings + res["warnings"]
        res["stage"]    = 1
        logger.info("Stage 1 berhasil.")
        return res

    if abort_requested:
        active_stage = 0
        return {"status": "FAILED", "errors": ["Generate dibatalkan oleh pengguna."], "warnings": []}

    # Stage 2 — kualifikasi kategori mapel sama
    logger.info("Stage 1 gagal. Stage 2: Fallback kualifikasi kategori...")
    active_stage = 2
    res = _run_solver(teachers, classes, allocations, ts_set, subjects_map,
                      stage=STAGE_CAT_QUAL, time_limit=90.0)
    if res:
        active_stage = 0
        res["warnings"] = warnings + res["warnings"]
        res["stage"]    = 2
        logger.info("Stage 2 berhasil.")
        return res

    if abort_requested:
        active_stage = 0
        return {"status": "FAILED", "errors": ["Generate dibatalkan oleh pengguna."], "warnings": []}

    # Skip Stage 3 karena ukuran model yang terlampau besar tanpa kualifikasi 
    # menyebabkan crash Access Violation (0xC0000005) pada platform Windows.
    # Sistem langsung mengalihkan ke diagnosa ketidaklayakan data (infeasibility diagnostics).
    logger.info("Stage 2 gagal. Melewati Stage 3 untuk menghindari crash memory. Menjalankan diagnosa...")

    diagnostics = _diagnose_infeasibility(teachers, classes, allocations, ts_set, subjects_map)
    return {
        "status":  "FAILED",
        "stage":   None,
        "errors":  [
            "Solver tidak dapat menemukan solusi yang layak (Infeasible) "
            "setelah 2 tahap pencarian. Periksa pesan kesalahan diagnosa di bawah "
            "untuk memperbaiki data master Anda."
        ] + diagnostics,
        "warnings": warnings,
    }
