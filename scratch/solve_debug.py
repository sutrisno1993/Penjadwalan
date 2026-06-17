import sys
import json
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch
from backend.solver import _fetch_master_data, _build_candidates, STAGE_FULL_QUAL, DAYS_ORDER, SHIFT_LIMITS, _slot_time, cp_model

def main():
    active_branch.set("bekasi")
    print("Fetching master data...")
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    classes_map = {c["id_kelas"]: c for c in classes}
    candidates = _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, STAGE_FULL_QUAL)
    
    model = cp_model.CpModel()
    x = {}
    teachers_map = {t["id_guru"]: t for t in teachers}
    
    for c in classes:
        cid = c["id_kelas"]
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
                            allowed_jp = t["allowed_jp_pagi"] if shift == "PAGI" else t["allowed_jp_siang"]
                            if allowed_jp and isinstance(allowed_jp, dict):
                                allowed_jps_for_day = allowed_jp.get(day) or allowed_jp.get(day.upper()) or allowed_jp.get(day.lower())
                                if allowed_jps_for_day is not None:
                                    if jp not in allowed_jps_for_day:
                                        continue
                                        
                            key = (cid, day, jp, aid, tid)
                            x[key] = model.NewBoolVar(f"x_c{cid}_{day}_jp{jp}_a{aid}_t{tid}")
                            
    # Lookup dictionaries
    by_class_slot = {}
    by_alloc = {}
    by_aid_tid = {}
    by_class_day_jp_aid = {}
    
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp), []).append(var)
        by_alloc.setdefault((cid, aid), []).append(var)
        by_aid_tid.setdefault((aid, tid), []).append(var)
        by_class_day_jp_aid.setdefault((cid, day, jp, aid), []).append(var)

    # C1: Max 1 pelajaran per slot kelas
    for c in classes:
        cid = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                vs = by_class_slot.get((cid, day, jp), [])
                if vs:
                    model.Add(sum(vs) <= 1).WithName(f"C1_c{cid}_{day}_jp{jp}")
                    
    # C2: Durasi JP per alokasi
    for a in allocations:
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        vs = by_alloc.get((cid, aid), [])
        if vs:
            model.Add(sum(vs) == a["durasi_jp"]).WithName(f"C2_c{cid}_a{aid}_dur{a['durasi_jp']}")
        elif a["durasi_jp"] > 0:
            print(f"ERROR: Allocation {aid} has no candidates!")
            
    # C2b: 1 Kelas + 1 Mapel = hanya 1 Guru
    for a in allocations:
        aid = a["id_class_subject"]
        cands = candidates.get(aid, [])
        if not cands:
            continue
            
        g_vars = {}
        for tid in cands:
            gv = model.NewBoolVar(f"g_{aid}_{tid}")
            g_vars[tid] = gv
            for var in by_aid_tid.get((aid, tid), []):
                model.Add(var <= gv).WithName(f"C2b_a{aid}_t{tid}_gv")
        if a["durasi_jp"] > 0:
            model.Add(sum(g_vars.values()) == 1).WithName(f"C2b_a{aid}_one_teacher")
            
    # C3: No Teacher Clash (wall-clock)
    for day in DAYS_ORDER:
        tid_keys = {}
        for c in classes:
            cid = c["id_kelas"]
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
                    time_pts.add(s)
                    time_pts.add(e)
                    
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
                    model.Add(sum(overlap_vars) <= 1).WithName(f"C3_t{tid}_{day}_overlap_{t0}_{t1}")
                    
    # C4: Olahraga - 2 JP berturut-turut
    for a in allocations:
        if not (any(kw in (a["nama_mapel"] or "").upper() for kw in ("JASMANI", "OLAH RAGA", "PENJASORKES", "OLAHRAGA", "PJOK"))):
            continue
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        shift = classes_map[cid]["shift_operasional"]
        
        y_blocks = {}
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for start in [1, 2, 3, 5] + ([6] if max_jp >= 7 else []):
                if start + 1 > max_jp:
                    continue
                if (by_class_day_jp_aid.get((cid, day, start, aid)) and
                        by_class_day_jp_aid.get((cid, day, start + 1, aid))):
                    yv = model.NewBoolVar(f"y_{cid}_{aid}_{day}_{start}")
                    y_blocks[(day, start)] = yv
                    
        if not y_blocks:
            print(f"ERROR: No valid block for Olahraga in class {a['nama_kelas']}")
            continue
            
        model.Add(sum(y_blocks.values()) == 1).WithName(f"C4_oly_c{cid}_a{aid}_one_block")
        
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for jp in range(1, max_jp + 1):
                covering = []
                if (day, jp) in y_blocks: covering.append(y_blocks[(day, jp)])
                if (day, jp - 1) in y_blocks: covering.append(y_blocks[(day, jp - 1)])
                slot_vars = by_class_day_jp_aid.get((cid, day, jp, aid), [])
                if slot_vars:
                    if covering:
                        model.Add(sum(slot_vars) == sum(covering)).WithName(f"C4_oly_c{cid}_a{aid}_{day}_jp{jp}_cov")
                    else:
                        model.Add(sum(slot_vars) == 0).WithName(f"C4_oly_c{cid}_a{aid}_{day}_jp{jp}_nocov")

    # C5: Lapangan Olahraga Capacity (Maks 1)
    olahraga_keys = []
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        a = next(al for al in allocations if al["id_class_subject"] == aid)
        if any(kw in (a["nama_mapel"] or "").upper() for kw in ("JASMANI", "OLAH RAGA", "PENJASORKES", "OLAHRAGA", "PJOK")):
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
                model.Add(sum(overlap_vars) <= 1).WithName(f"C5_oly_field_{day}_{t0}_{t1}")

    # Teacher loads and min/max jp
    for tid in {tid for (_, _, _, _, tid) in x}:
        all_t_vars = [var for key, var in x.items() if key[4] == tid]
        if all_t_vars:
            load = model.NewIntVar(0, 200, f"load_{tid}")
            model.Add(load == cp_model.LinearExpr.Sum(all_t_vars))
            t_info = teachers_map[tid]
            min_jp_val = t_info.get("min_jp")
            max_jp_val = t_info.get("max_jp")
            
            is_active = model.NewBoolVar(f"active_{tid}")
            model.Add(load <= 200 * is_active)
            model.Add(load >= is_active)
            
            if min_jp_val is not None:
                model.Add(load >= min_jp_val * is_active).WithName(f"C_min_jp_t{tid}")
                if min_jp_val > 10:
                    model.Add(is_active == 1)
            if max_jp_val is not None:
                model.Add(load <= max_jp_val).WithName(f"C_max_jp_t{tid}")

    print("Solving with 1 worker...")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    print(f"Status: {solver.StatusName(status)}")
    print(solver.ResponseStats())

if __name__ == "__main__":
    main()
