import os
import json
import logging
from dotenv import load_dotenv
from ortools.sat.python import cp_model
from backend.database import get_db_connection, db_fetchall
from backend.solver import _fetch_master_data, _sort_allocations, _build_candidates, STAGE_SHIFT_ONLY, DAYS_ORDER, SHIFT_LIMITS, _slot_time, _is_olahraga, _is_produktif

load_dotenv()
logging.basicConfig(level=logging.INFO)

def run_relax_solver(
    disable_teacher_clash=False,
    disable_olahraga_block=False,
    disable_olahraga_field=False,
    disable_teacher_avail=False,
    disable_teacher_max_load=False,
    disable_teacher_min_load=False,
    disable_locked_teachers=False,
    disable_one_teacher_per_alloc=False
):
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    
    # Optional: disable locked teachers by setting id_guru_mutlak = None
    if disable_locked_teachers:
        for a in allocations:
            a["id_guru_mutlak"] = None

    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    allocations_map = {a["id_class_subject"]: a for a in allocations}

    # Stage 3 candidates: all available teachers in correct shift
    candidates = _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, STAGE_SHIFT_ONLY)

    model = cp_model.CpModel()
    x = {}

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
                        t = teachers_map[tid]
                        
                        if not disable_teacher_avail:
                            avail = t["hari_tersedia_pagi"] if shift == "PAGI" else t["hari_tersedia_siang"]
                            if day not in avail:
                                continue
                            allowed_jp = t["allowed_jp_pagi"] if shift == "PAGI" else t["allowed_jp_siang"]
                            if allowed_jp and isinstance(allowed_jp, dict):
                                allowed_jps_for_day = allowed_jp.get(day) or allowed_jp.get(day.upper()) or allowed_jp.get(day.lower())
                                if allowed_jps_for_day is not None and jp not in allowed_jps_for_day:
                                    continue

                        key = (cid, day, jp, aid, tid)
                        x[key] = model.NewBoolVar(f"x_c{cid}_{day}_jp{jp}_a{aid}_t{tid}")

    # Lookup dicts
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

    # Constraint 1: Max 1 lesson per slot per class
    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                vs = by_class_slot.get((cid, day, jp), [])
                if vs:
                    model.Add(sum(vs) <= 1)

    # Constraint 2: Durasi JP per alokasi
    for a in allocations:
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        vs  = by_alloc.get((cid, aid), [])
        if vs:
            model.Add(sum(vs) == a["durasi_jp"])
        elif a["durasi_jp"] > 0:
            return "infeasible_no_candidates"

    # Constraint 2b: 1 Kelas + 1 Mapel = hanya 1 Guru
    if not disable_one_teacher_per_alloc:
        for a in allocations:
            aid = a["id_class_subject"]
            cands = candidates.get(aid, [])
            if not cands:
                continue
            g_vars = {}
            for tid in cands:
                gv = model.NewBoolVar(f"g_a{aid}_t{tid}")
                g_vars[tid] = gv
                for var in by_aid_tid.get((aid, tid), []):
                    model.Add(var <= gv)
            if a["durasi_jp"] > 0:
                model.Add(sum(g_vars.values()) == 1)
            else:
                model.Add(sum(g_vars.values()) == 0)

    # Constraint 3: No Teacher Clash
    if not disable_teacher_clash:
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

    # Constraint 4: Olahraga - block 2 JP berturut-turut
    if not disable_olahraga_block:
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

            if not y_blocks:
                return f"infeasible_olahraga_block_no_slots_for_{a['nama_kelas']}"

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

    # Constraint 5: Olahraga Field Capacity
    if not disable_olahraga_field:
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

    # Teacher loads variables
    teacher_load_vars = {}
    for tid in {tid for (_, _, _, _, tid) in x}:
        all_t_vars = [var for key, var in x.items() if key[4] == tid]
        if all_t_vars:
            load = model.NewIntVar(0, 200, f"load_{tid}")
            model.Add(load == sum(all_t_vars))
            teacher_load_vars[tid] = load

    # Teacher load bounds
    for tid, load in teacher_load_vars.items():
        t_info = teachers_map[tid]
        min_jp_val = t_info.get("min_jp")
        max_jp_val = t_info.get("max_jp")
        
        is_active = model.NewBoolVar(f"active_{tid}")
        model.Add(load <= 200 * is_active)
        model.Add(load >= is_active)
        
        if not disable_teacher_min_load and min_jp_val is not None:
            model.Add(load >= min_jp_val * is_active)
            if min_jp_val > 10:
                model.Add(is_active == 1)
        
        if not disable_teacher_max_load and max_jp_val is not None:
            model.Add(load <= max_jp_val)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "feasible"
    else:
        return "infeasible"

if __name__ == "__main__":
    print("Testing regular Stage 3 solver...")
    print("Result:", run_relax_solver())
    
    print("\nRelaxing one by one...")
    scenarios = [
        ("disable_teacher_clash", {"disable_teacher_clash": True}),
        ("disable_olahraga_block", {"disable_olahraga_block": True}),
        ("disable_olahraga_field", {"disable_olahraga_field": True}),
        ("disable_teacher_avail", {"disable_teacher_avail": True}),
        ("disable_teacher_max_load", {"disable_teacher_max_load": True}),
        ("disable_teacher_min_load", {"disable_teacher_min_load": True}),
        ("disable_locked_teachers", {"disable_locked_teachers": True}),
        ("disable_one_teacher_per_alloc", {"disable_one_teacher_per_alloc": True}),
    ]
    
    for name, args in scenarios:
        res = run_relax_solver(**args)
        print(f"Scenario '{name}': {res}")
        
    print("\nTesting multiple relaxations...")
    # Test combination of locked teachers + other constraints
    print("Relaxing BOTH locked teachers AND teacher availability:", run_relax_solver(disable_locked_teachers=True, disable_teacher_avail=True))
    print("Relaxing BOTH locked teachers AND teacher clash:", run_relax_solver(disable_locked_teachers=True, disable_teacher_clash=True))
    print("Relaxing BOTH locked teachers AND olahraga block:", run_relax_solver(disable_locked_teachers=True, disable_olahraga_block=True))
