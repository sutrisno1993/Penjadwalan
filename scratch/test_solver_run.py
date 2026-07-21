import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection
from backend.solver import _fetch_master_data, _build_candidates, STAGE_FULL_QUAL, SHIFT_LIMITS, DAYS_ORDER
from ortools.sat.python import cp_model

def main():
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()

    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    allocations_map = {a["id_class_subject"]: a for a in allocations}

    candidates = _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, STAGE_FULL_QUAL)

    model = cp_model.CpModel()
    x = {}

    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                for a in allocations:
                    if a["id_kelas"] != cid:
                        continue
                    aid   = a["id_class_subject"]
                    cands = candidates.get(aid, [])
                    for tid in cands:
                        t = teachers_map[tid]
                        # Availability check
                        days_avail = t.get("hari_tersedia_pagi", []) if shift == "PAGI" else t.get("hari_tersedia_siang", [])
                        if day not in days_avail:
                            continue
                        
                        var = model.NewBoolVar(f"x_{cid}_{day}_{jp}_{aid}_{tid}")
                        x[(cid, day, jp, aid, tid)] = var

    # 1. Slot Constraint
    by_class_slot = {}
    by_alloc = {}
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp), []).append(var)
        by_alloc.setdefault((cid, aid), []).append(var)

    for (cid, day, jp), vs in by_class_slot.items():
        model.Add(sum(vs) <= 1)

    # 2. Duration Constraint
    for a in allocations:
        cid = a["id_kelas"]
        aid = a["id_class_subject"]
        vs  = by_alloc.get((cid, aid), [])
        if vs:
            model.Add(sum(vs) == a["durasi_jp"])
        else:
            print(f"❌ NO CANDIDATE FOR ALLOCATION {aid}: {a['nama_kelas']} - {a['nama_mapel']}")

    # 3. Teacher collision (1 teacher can only be in 1 class at any single slot)
    by_teacher_slot = {}
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        c = classes_map[cid]
        shift = c["shift_operasional"]
        by_teacher_slot.setdefault((tid, shift, day, jp), []).append(var)

    for (tid, shift, day, jp), vs in by_teacher_slot.items():
        if len(vs) > 1:
            model.Add(sum(vs) <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.log_search_progress = True
    
    print("\n--- SOLVING CP-SAT MODEL ---")
    status = solver.Solve(model)
    print(f"Status: {solver.StatusName(status)}")
    print(f"Stats: {solver.ResponseStats()}")

if __name__ == '__main__':
    main()
