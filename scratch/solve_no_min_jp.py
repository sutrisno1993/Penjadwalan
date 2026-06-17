import os
import time
from dotenv import load_dotenv
from ortools.sat.python import cp_model
from backend.database import get_db_connection, db_fetchall
from backend.solver import _fetch_master_data, _slot_time, _is_olahraga, DAYS_ORDER, SHIFT_LIMITS

load_dotenv()

def run_test():
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    
    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    allocations_map = {a["id_class_subject"]: a for a in allocations}

    # Stage 1 candidates
    candidates = {}
    for a in allocations:
        shift    = classes_map[a["id_kelas"]]["shift_operasional"]
        id_mapel = a["id_mapel"]
        cands    = []
        for t in teachers:
            tid = t["id_guru"]
            if not ((shift == "PAGI" and t["shift_pagi"]) or (shift == "SIANG" and t["shift_siang"])):
                continue
            if not ts_set or (tid, id_mapel) not in ts_set:
                continue
            cands.append(tid)
        
        # Ensure locked teacher is in candidates
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed and id_fixed not in cands:
            cands.append(id_fixed)
            
        candidates[a["id_class_subject"]] = cands

    model = cp_model.CpModel()
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
                        avail = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                        if day in avail:
                            key = (cid, day, jp, aid, tid)
                            x[key] = model.NewBoolVar(f"x_c{cid}_{day}_jp{jp}_a{aid}_t{tid}")

    by_class_slot = {}
    by_alloc_slot = {}
    by_alloc = {}
    by_teacher_day = {}
    by_aid_tid = {}

    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp), []).append(var)
        by_alloc_slot.setdefault((cid, day, jp, aid), []).append(var)
        by_alloc.setdefault((cid, aid), []).append(var)
        by_teacher_day.setdefault((tid, day), []).append(key)
        by_aid_tid.setdefault((aid, tid), []).append(var)

    # 1. No Class Clash
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
            model.Add(sum(vs) == a["durasi_jp"])

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
        model.Add(sum(g_vars.values()) == 1)

        # Locked teacher constraint
        id_fixed = a.get("id_guru_mutlak")
        if id_fixed and id_fixed in g_vars:
            model.Add(g_vars[id_fixed] == 1)

    # 4. No Teacher Clash (wall-clock)
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
                    model.Add(sum(overlap_vars) <= 1)

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

    # 6. Olahraga Field Capacity (Maks 1 kelas bersamaan)
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
                model.Add(sum(overlap_vars) <= 1)

    # 7. Teacher load limits (EXCLUDING min_jp constraint)
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
        
        is_active = model.NewBoolVar(f"active_{tid}")
        model.Add(load <= 200 * is_active)
        model.Add(load >= is_active)
        
        if max_jp_val is not None:
            model.Add(load <= max_jp_val)

    print("Solving model WITHOUT min_jp constraints...")
    t0 = time.time()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 20.0
    status = solver.Solve(model)
    t1 = time.time()
    
    print(f"Status: {solver.StatusName(status)} (took {t1 - t0:.2f} seconds)")
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("FEASIBLE schedule found successfully without min_jp constraints!")

if __name__ == "__main__":
    run_test()
