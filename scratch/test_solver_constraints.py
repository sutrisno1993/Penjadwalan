import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.solver import _fetch_master_data, _build_candidates, STAGE_FULL_QUAL, SHIFT_LIMITS, DAYS_ORDER
from ortools.sat.python import cp_model

def run_test(enable_max_jp_per_day=True, enable_split_multi=True, enable_single_teacher=True):
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
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
                        days_avail = t.get("hari_tersedia_pagi", []) if shift == "PAGI" else t.get("hari_tersedia_siang", [])
                        if day not in days_avail:
                            continue
                        var = model.NewBoolVar(f"x_{cid}_{day}_{jp}_{aid}_{tid}")
                        x[(cid, day, jp, aid, tid)] = var

    # 1. Slot Constraint
    by_class_slot = {}
    by_alloc = {}
    by_aid_tid = {}
    by_class_teacher_day = {}
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        by_class_slot.setdefault((cid, day, jp), []).append(var)
        by_alloc.setdefault((cid, aid), []).append(var)
        by_aid_tid.setdefault((aid, tid), []).append(var)
        by_class_teacher_day.setdefault((cid, tid, day), []).append(var)

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
            return "NO_CANDIDATE"

    # 3. Teacher overlap
    by_teacher_slot = {}
    for key, var in x.items():
        cid, day, jp, aid, tid = key
        c = classes_map[cid]
        shift = c["shift_operasional"]
        by_teacher_slot.setdefault((tid, shift, day, jp), []).append(var)

    for (tid, shift, day, jp), vs in by_teacher_slot.items():
        if len(vs) > 1:
            model.Add(sum(vs) <= 1)

    # Constraint A: Single Teacher per Allocation
    if enable_single_teacher:
        for a in allocations:
            aid = a["id_class_subject"]
            cands = candidates.get(aid, [])
            if not cands: continue
            g_vars = {}
            for tid in cands:
                gv = model.NewBoolVar(f"g_a{aid}_t{tid}")
                g_vars[tid] = gv
                for var in by_aid_tid.get((aid, tid), []):
                    model.Add(var <= gv)

    # Constraint B: Max 4 JP per day per class
    if enable_max_jp_per_day:
        for (cid, tid, day), vars_list in by_class_teacher_day.items():
            if vars_list:
                model.Add(sum(vars_list) <= 4)

    # Constraint C: Split Multi-Subject
    if enable_split_multi:
        class_teacher_allocs = {}
        for a in allocations:
            aid = a["id_class_subject"]
            cid = a["id_kelas"]
            cands = candidates.get(aid, [])
            for tid in cands:
                class_teacher_allocs.setdefault((cid, tid), []).append(a)

        for (cid, tid), allocs_ct in class_teacher_allocs.items():
            if len(allocs_ct) >= 2:
                tot_jp = sum(a["durasi_jp"] for a in allocs_ct)
                if tot_jp > 5:
                    for day in DAYS_ORDER:
                        aid_active_vars = []
                        for a in allocs_ct:
                            aid = a["id_class_subject"]
                            jp_vars = [
                                var for key, var in x.items()
                                if key[0] == cid and key[1] == day and key[3] == aid and key[4] == tid
                            ]
                            if jp_vars:
                                is_active = model.NewBoolVar(f"multi_split_c{cid}_t{tid}_a{aid}_{day}")
                                model.Add(sum(jp_vars) >= 1).OnlyEnforceIf(is_active)
                                model.Add(sum(jp_vars) == 0).OnlyEnforceIf(is_active.Not())
                                aid_active_vars.append(is_active)

                        if len(aid_active_vars) > 1:
                            model.Add(sum(aid_active_vars) <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)
    return solver.StatusName(status)

def main():
    print("Testing combinations of constraints:")
    res1 = run_test(enable_max_jp_per_day=True, enable_split_multi=False, enable_single_teacher=True)
    print(f"1. Max 4 JP/day + Single Teacher (No Split Multi) => {res1}")

    res2 = run_test(enable_max_jp_per_day=True, enable_split_multi=True, enable_single_teacher=True)
    print(f"2. Max 4 JP/day + Single Teacher + Split Multi    => {res2}")

    res3 = run_test(enable_max_jp_per_day=False, enable_split_multi=True, enable_single_teacher=True)
    print(f"3. No Max JP Limit + Single Teacher + Split Multi => {res3}")

if __name__ == '__main__':
    main()
