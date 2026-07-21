import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.solver import _fetch_master_data

def main():
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()

    pagi_cids = set(c["id_kelas"] for c in classes if c.get("shift_operasional") == "PAGI")
    siang_cids = set(c["id_kelas"] for c in classes if c.get("shift_operasional") == "SIANG")

    # Group allocations by teacher
    teacher_allocs = {}
    for a in allocations:
        gid = a.get("id_guru_mutlak")
        if gid:
            teacher_allocs.setdefault(gid, []).append(a)

    print("--- DETAILED PER-TEACHER CAPACITY AND WORKLOAD ---")
    
    total_pagi_capacity = 0
    total_siang_capacity = 0

    for t in teachers:
        gid = t["id_guru"]
        allocs = teacher_allocs.get(gid, [])
        
        pagi_jp = sum(a["durasi_jp"] for a in allocs if a["id_kelas"] in pagi_cids)
        siang_jp = sum(a["durasi_jp"] for a in allocs if a["id_kelas"] in siang_cids)
        total_jp = pagi_jp + siang_jp
        
        p_days = t.get("hari_tersedia_pagi", [])
        s_days = t.get("hari_tersedia_siang", [])
        
        # In a 6-day week:
        # Pagi has 7 JP per day (except Jumat 6 JP) = ~41 JP max per week if available 6 days
        # Siang has 7 JP per day (except Jumat/Sabtu 6 JP) = ~40 JP max per week if available 6 days
        # BUT a teacher can only be in 1 class at any single JP slot!
        
        # Max capacity for this teacher in Pagi: len(p_days) * 7 (if max 7 JP/day)
        # Max capacity for this teacher in Siang: len(s_days) * 7 (if max 7 JP/day)
        
        pagi_cap = len(p_days) * 7
        siang_cap = len(s_days) * 7
        
        total_pagi_capacity += pagi_cap
        total_siang_capacity += siang_cap
        
        status = "OK"
        if pagi_jp > pagi_cap or siang_jp > siang_cap:
            status = "❌ OVERLOAD (BENTROK JADWAL HASILNYA INFEASIBLE)"
            
        print(f"Guru {t['kode_guru']:2}: {t['nama_guru']:30} | Pagi: {pagi_jp:2} JP (Hari: {len(p_days)}) | Siang: {siang_jp:2} JP (Hari: {len(s_days)}) | Total: {total_jp:2} JP | Status: {status}")

    print(f"\n--- CAPACITY SUMMARY ---")
    print(f"Total Kapasitas Pagi Maksimal  : {total_pagi_capacity} JP  (Dibutuhkan: 400 JP)")
    print(f"Total Kapasitas Siang Maksimal : {total_siang_capacity} JP  (Dibutuhkan: 600 JP)")

if __name__ == '__main__':
    main()
