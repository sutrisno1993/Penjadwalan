import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection
from backend.solver import _fetch_master_data, _build_candidates, STAGE_FULL_QUAL, SHIFT_LIMITS, DAYS_ORDER, _is_olahraga

def main():
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    teachers_map = {t["id_guru"]: t for t in teachers}
    classes_map  = {c["id_kelas"]: c for c in classes}
    candidates = _build_candidates(teachers, classes_map, allocations, ts_set, subjects_map, STAGE_FULL_QUAL)

    by_alloc_slot = {}
    for c in classes:
        cid   = c["id_kelas"]
        shift = c["shift_operasional"]
        for day in DAYS_ORDER:
            for jp in range(1, SHIFT_LIMITS[shift].get(day, 0) + 1):
                for a in allocations:
                    if a["id_kelas"] != cid: continue
                    aid   = a["id_class_subject"]
                    cands = candidates.get(aid, [])
                    for tid in cands:
                        t = teachers_map[tid]
                        days_avail = t.get("hari_tersedia_pagi", []) if shift == "PAGI" else t.get("hari_tersedia_siang", [])
                        if day in days_avail:
                            by_alloc_slot.setdefault((cid, day, jp, aid), []).append(tid)

    print("--- CHECKING OLAHRAGA BLOCK AVAILABILITY ---")
    for a in allocations:
        if not _is_olahraga(a["nama_mapel"], a["kategori_mapel"]):
            continue
        cid   = a["id_kelas"]
        aid   = a["id_class_subject"]
        shift = classes_map[cid]["shift_operasional"]
        
        y_blocks = []
        for day in DAYS_ORDER:
            max_jp = SHIFT_LIMITS[shift].get(day, 0)
            for start in [1, 2, 3, 5] + ([6] if max_jp >= 7 else []):
                if start + 1 > max_jp: continue
                if (by_alloc_slot.get((cid, day, start, aid)) and
                        by_alloc_slot.get((cid, day, start + 1, aid))):
                    y_blocks.append((day, start))
        
        if not y_blocks:
            print(f"❌ OLAHRAGA HARD ERROR: Class {a['nama_kelas']} - Mapel {a['nama_mapel']} (ID {aid}) HAS NO VALID 2-JP BLOCK!")
        else:
            print(f"✅ Class {a['nama_kelas']} - Mapel {a['nama_mapel']}: {len(y_blocks)} valid blocks.")

if __name__ == '__main__':
    main()
