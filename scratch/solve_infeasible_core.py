import sys
sys.path.insert(0, 'd:/Jadwal')
import os
import json
from dotenv import load_dotenv
from ortools.sat.python import cp_model
from backend.database import get_db_connection, db_fetchall
from backend.solver import _fetch_master_data, _sort_allocations, _build_candidates, STAGE_SHIFT_ONLY, DAYS_ORDER, SHIFT_LIMITS, _slot_time, _is_olahraga, _is_produktif

load_dotenv()

def find_infeasible_core():
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    
    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    allocations_map = {a["id_class_subject"]: a for a in allocations}

    # Build candidates: allow only qualified teachers (STAGE_FULL_QUAL)
    # but we DO NOT restrict by id_guru_mutlak in candidates dict.
    # Instead, we will add a constraint for id_guru_mutlak and associate an assumption variable with it!
    candidates = {}
    for a in allocations:
        shift    = classes_map[a["id_kelas"]]["shift_operasional"]
        id_mapel = a["id_mapel"]
        cands    = []
        for t in teachers:
            tid = t["id_guru"]
            # Filter shift
            if not ((shift == "PAGI" and t["shift_pagi"]) or
                    (shift == "SIANG" and t["shift_siang"])):
                continue
            # Filter qualification
            if not ts_set or (tid, id_mapel) not in ts_set:
                continue
            cands.append(tid)
        
        # Ensure locked teacher is in candidates
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed and id_fixed not in cands:
            cands.append(id_fixed)
            
        candidates[a["id_class_subject"]] = cands

    model = cp_model.CpModel()
    
    # Assumption variables maps
    assumptions = []
    assump_desc = {}

    def new_assump(desc):
        var = model.NewBoolVar(f"as_{len(assumptions)}")
        assumptions.append(var)
        assump_desc[var.Index()] = desc
        return var

    x = {}
    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        c_allocs = [a for a in allocations if a["id_kelas"] == cid]

        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for jp in range(1, max_jp + 1):
                if day == "SENIN" and jp == 1 and shift == "PAGI":
                    continue

                for a in c_allocs:
                    aid = a["id_class_subject"]
                    for tid in candidates.get(aid, []):
                        t = teachers_map[tid]
                        # Check teacher available day
                        avail = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                        if day in avail:
                            key = (cid, day, jp, aid, tid)
                            x[key] = model.NewBoolVar(f"x_c{cid}_{day}_jp{jp}_a{aid}_t{tid}")

    by_class_slot = {}
    by_alloc_slot = {}
    by_alloc = {}
    by_alloc_day = {}
    by_teacher_day = {}
    by_aid_tid = {}

    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp), []).append(var)
        by_alloc_slot.setdefault((cid, day, jp, aid), []).append(var)
        by_alloc.setdefault((cid, aid), []).append(var)
        by_alloc_day.setdefault((cid, aid, day), []).append(var)
        by_teacher_day.setdefault((tid, day), []).append(key)
        by_aid_tid.setdefault((aid, tid), []).append(var)

    # 1. No Class Clash: Max 1 lesson per slot per class
    # (This is a physical constraint, we do not relax this)
    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                vs = by_class_slot.get((cid, day, jp), [])
                if vs:
                    model.Add(sum(vs) <= 1)

    # 2. Durasi JP per alokasi
    for a in allocations:
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        vs  = by_alloc.get((cid, aid), [])
        if vs:
            as_var = new_assump(f"Durasi JP untuk Kelas {a['nama_kelas']} Mapel {a['nama_mapel']} (butuh {a['durasi_jp']} JP)")
            model.Add(sum(vs) == a["durasi_jp"]).OnlyEnforceIf(as_var)

    # 3. 1 Kelas + 1 Mapel = hanya 1 Guru
    for a in allocations:
        aid = a["id_class_subject"]
        cands = candidates.get(aid, [])
        if not cands or a["durasi_jp"] <= 0:
            continue
        g_vars = {}
        for tid in cands:
            gv = model.NewBoolVar(f"g_a{aid}_t{tid}")
            g_vars[tid] = gv
            for var in by_aid_tid.get((aid, tid), []):
                model.Add(var <= gv)
                
        as_var = new_assump(f"Tepat 1 guru untuk Kelas {a['nama_kelas']} Mapel {a['nama_mapel']}")
        model.Add(sum(g_vars.values()) == 1).OnlyEnforceIf(as_var)

        # Locked teacher constraint: if there is id_guru_mutlak, force g_vars[id_guru_mutlak] == 1
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed and id_fixed in g_vars:
            t_fixed = teachers_map[id_fixed]
            as_lock = new_assump(f"Locked guru [{t_fixed['nama_guru']}] untuk Kelas {a['nama_kelas']} Mapel {a['nama_mapel']}")
            model.Add(g_vars[id_fixed] == 1).OnlyEnforceIf(as_lock)

    # 4. No Teacher Clash
    for day in DAYS_ORDER:
        tid_keys = {}
        for c in classes:
            cid   = c["id_kelas"]
            shift = c["shift_operasional"]
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                for a in [al for al in allocations if al["id_kelas"] == cid]:
                    for tid in candidates.get(a["id_class_subject"], []):
                        key = (cid, day, jp, a["id_class_subject"], tid)
                        if key in x:
                            tid_keys.setdefault(tid, []).append(key)

        time_pts = set()
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
                    t_info = teachers_map[tid]
                    as_var = new_assump(f"No Teacher Clash: {t_info['nama_guru']} pada {day} menit {t0}-{t1}")
                    model.Add(sum(overlap_vars) <= 1).OnlyEnforceIf(as_var)

    # 5. Olahraga - block 2 JP berturut-turut
    for a in allocations:
        if not _is_olahraga(a["nama_mapel"], a["kategori_mapel"]):
            continue
        cid   = a["id_kelas"]
        aid   = a["id_class_subject"]
        shift = classes_map[cid]["shift_operasional"]

        y_blocks = {}
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for start in [1, 2, 3, 5] + ([6] if max_jp >= 7 else []):
                if start + 1 > max_jp:
                    continue
                if (by_alloc_slot.get((cid, day, start, aid)) and
                        by_alloc_slot.get((cid, day, start + 1, aid))):
                    yv = model.NewBoolVar(f"y_c{cid}_a{aid}_{day}_s{start}")
                    y_blocks[(day, start)] = yv

        if y_blocks:
            as_var = new_assump(f"Olahraga Block 2 JP untuk {a['nama_kelas']}")
            model.Add(sum(y_blocks.values()) == 1).OnlyEnforceIf(as_var)

            for day in DAYS_ORDER:
                max_jp = SHIFT_LIMITS[shift].get(day, 0)
                for jp in range(1, max_jp + 1):
                    covering = []
                    if (day, jp)     in y_blocks: covering.append(y_blocks[(day, jp)])
                    if (day, jp - 1) in y_blocks: covering.append(y_blocks[(day, jp - 1)])
                    slot_vars = by_alloc_slot.get((cid, day, jp, aid), [])
                    if slot_vars:
                        if covering:
                            model.Add(sum(slot_vars) == sum(covering)).OnlyEnforceIf(as_var)
                        else:
                            model.Add(sum(slot_vars) == 0).OnlyEnforceIf(as_var)

    # 6. Olahraga Field Capacity
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
                time_pts.add(s); time_pts.add(e)
                
        sorted_pts = sorted(time_pts)
        for t0, t1 in zip(sorted_pts, sorted_pts[1:]):
            overlap_vars = []
            for key in day_oly_keys:
                cid, _, jp, _, _ = key
                s, e = _slot_time(day, classes_map[cid]["shift_operasional"], jp)
                if s < t1 and e > t0:
                    overlap_vars.append(x[key])
            if len(overlap_vars) > 1:
                as_var = new_assump(f"Lapangan Olahraga Maks 1 Kelas: {day} menit {t0}-{t1}")
                model.Add(sum(overlap_vars) <= 1).OnlyEnforceIf(as_var)

    # 7. Teacher load limits
    teacher_load_vars = {}
    for tid in {tid for (_, _, _, _, tid) in x}:
        all_t_vars = [var for key, var in x.items() if key[4] == tid]
        if all_t_vars:
            load = model.NewIntVar(0, 200, f"load_{tid}")
            model.Add(load == sum(all_t_vars))
            teacher_load_vars[tid] = load

    for tid, load in teacher_load_vars.items():
        t_info = teachers_map[tid]
        max_jp_val = t_info.get("max_jp")
        if max_jp_val is not None:
            as_var = new_assump(f"Max JP Guru {t_info['nama_guru']} ({max_jp_val} JP)")
            model.Add(load <= max_jp_val).OnlyEnforceIf(as_var)

    # Solve with assumptions
    model.AddAssumptions(assumptions)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)
    
    if status == cp_model.INFEASIBLE:
        print("\n=== SOLVER INFEASIBLE: SUFFICIENT INFEASIBLE CORE ===")
        core = solver.SufficientAssumptionsForInfeasibility()
        for c in core:
            print(f" - {assump_desc.get(c, 'Unknown constraint')}")
    elif status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("\n=== SOLVER FEASIBLE WITH ALL ASSUMPTIONS ACTIVE ===")
    else:
        print(f"\nSolver status: {status} (No solution found within time limit)")

if __name__ == "__main__":
    find_infeasible_core()
