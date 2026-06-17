import sys
sys.path.insert(0, 'd:/Jadwal')
import json
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')
from backend.database import get_db_connection
from backend.main import DAYS_ORDER, SHIFT_LIMITS

def diagnose():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Fetch Classes
    cur.execute("SELECT id_kelas, nama_kelas, shift_operasional FROM classes")
    classes = cur.fetchall()
    classes_map = {c["id_kelas"]: c for c in classes}
    
    # 2. Fetch Teachers
    cur.execute("SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp, allowed_jp_pagi, allowed_jp_siang FROM teachers")
    teachers = cur.fetchall()
    for t in teachers:
        t["hari_tersedia_pagi"] = json.loads(t["hari_tersedia_pagi"] or "[]")
        t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
        t["allowed_jp_pagi"] = json.loads(t["allowed_jp_pagi"]) if t.get("allowed_jp_pagi") else None
        t["allowed_jp_siang"] = json.loads(t["allowed_jp_siang"]) if t.get("allowed_jp_siang") else None
    
    teachers_map = {t["id_guru"]: t for t in teachers}
    
    # 3. Fetch Allocations
    cur.execute("""
        SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
               c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
    """)
    allocations = cur.fetchall()
    
    print("=== DIAGNOSA DETAIL BOTTLENECK CONSTRAINT ===")
    
    # Check A: Total Kelas vs Guru per Shift per Hari (Daily Coverage)
    print("\n[A] Daily Coverage (Apakah jumlah kelas aktif melampaui jumlah guru yang bersedia hadir?)")
    for shift in ["PAGI", "SIANG"]:
        active_classes = [c for c in classes if c["shift_operasional"] == shift]
        n_kelas = len(active_classes)
        print(f"\nShift {shift} ({n_kelas} kelas aktif):")
        for day in DAYS_ORDER:
            # Hitung guru yang tersedia di shift & hari ini
            gurus_hadir = []
            for t in teachers:
                if shift == "PAGI" and t["shift_pagi"] and day in t["hari_tersedia_pagi"]:
                    gurus_hadir.append(t["nama_guru"])
                elif shift == "SIANG" and t["shift_siang"] and day in t["hari_tersedia_siang"]:
                    gurus_hadir.append(t["nama_guru"])
            
            n_guru = len(gurus_hadir)
            if n_guru < n_kelas:
                print(f"  [ERR] HARI {day}: Butuh {n_kelas} guru, tapi hanya ada {n_guru} guru tersedia!")
                print(f"     Guru yang tersedia: {', '.join(gurus_hadir) if gurus_hadir else 'TIDAK ADA'}")
            else:
                print(f"  [OK] HARI {day}: Tersedia {n_guru} guru (Butuh {n_kelas})")
                
    # Check B: Total Beban JP per Shift vs Total Kapasitas Guru per Shift
    print("\n[B] Total Beban JP vs Kapasitas Guru per Shift")
    for shift in ["PAGI", "SIANG"]:
        shift_allocs = [a for a in allocations if a["shift_operasional"] == shift]
        total_jp_demand = sum(a["durasi_jp"] for a in shift_allocs)
        
        # Max capacity of teachers in this shift
        total_max_capacity = 0
        active_teachers = []
        for t in teachers:
            if (shift == "PAGI" and t["shift_pagi"]) or (shift == "SIANG" and t["shift_siang"]):
                active_teachers.append(t)
                total_max_capacity += t["max_jp"] if t["max_jp"] is not None else 60
                
        print(f"Shift {shift}:")
        print(f"  Total Kebutuhan (Demand)  : {total_jp_demand} JP")
        print(f"  Total Kapasitas Guru (Max) : {total_max_capacity} JP")
        if total_jp_demand > total_max_capacity:
            print(f"  [ERR] Terjadi OVERLOAD! Kebutuhan JP ({total_jp_demand}) melampaui kapasitas maksimal guru ({total_max_capacity}).")
        else:
            print(f"  [OK] Kapasitas mencukupi.")

    # Check C: Batasan Jam Pelajaran Spesifik (allowed_jp_pagi / allowed_jp_siang)
    print("\n[C] Batasan Jam Pelajaran Spesifik (Guru yang membatasi jam mengajar mereka)")
    for t in teachers:
        has_restriction = False
        res_details = []
        for shift, allowed in [("PAGI", t["allowed_jp_pagi"]), ("SIANG", t["allowed_jp_siang"])]:
            if allowed:
                has_restriction = True
                for day, jps in allowed.items():
                    if len(jps) < SHIFT_LIMITS[shift].get(day, 0):
                        res_details.append(f"{shift} {day} hanya bisa JP {jps}")
        if has_restriction:
            # Let's count how many JP this teacher is assigned in allocations
            teacher_allocs = [a for a in allocations if a["id_guru_mutlak"] == t["id_guru"]]
            locked_jp = sum(a["durasi_jp"] for a in teacher_allocs)
            print(f"  - Guru: {t['nama_guru']} (Kode {t['kode_guru']})")
            print(f"    Beban Guru Mutlak: {locked_jp} JP")
            print(f"    Batasan: {'; '.join(res_details)}")

    # Check D: Olahraga Lapangan (PJOK) Overlap
    print("\n[D] Kapasitas Lapangan PJOK")
    for shift in ["PAGI", "SIANG"]:
        oly_allocs = [a for a in allocations if a["shift_operasional"] == shift and ("OLAHRAGA" in (a["kategori_mapel"] or "").upper() or "PJOK" in (a["nama_mapel"] or "").upper())]
        oly_demand = sum(a["durasi_jp"] for a in oly_allocs)
        max_oly_slots = sum(SHIFT_LIMITS[shift].get(d, 0) for d in DAYS_ORDER)
        print(f"Shift {shift}:")
        print(f"  Total JP Olahraga: {oly_demand} JP")
        print(f"  Batas Lapangan    : {max_oly_slots} JP")
        if oly_demand > max_oly_slots:
            print(f"  [ERR] Terjadi bentrokan lapangan! Total durasi {oly_demand} JP melampaui slot seminggu ({max_oly_slots} JP).")
        else:
            print(f"  [OK] Aman.")

    conn.close()

if __name__ == '__main__':
    diagnose()
