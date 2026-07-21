import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection
from backend.solver import _fetch_master_data, _preflight, _diagnose_infeasibility

def main():
    print("Fetching master data from current database in .env...")
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()

    print(f"\n--- DATA MASTER SUMMARY ---")
    print(f"Total Teachers    : {len(teachers)}")
    print(f"Total Classes     : {len(classes)}")
    print(f"Total Allocations : {len(allocations)}")
    print(f"Total Subjects    : {len(subjects_map)}")

    # 1. Run Preflight
    print("\n--- 1. RUNNING PREFLIGHT DIAGNOSIS ---")
    warnings, hard_errors = _preflight(teachers, classes, allocations, ts_set, subjects_map)
    
    if hard_errors:
        print("\n❌ HARD ERRORS (Inisialisasi Solver Gagal):")
        for idx, err in enumerate(hard_errors, 1):
            print(f"  {idx}. {err}")
    else:
        print("\n✅ Tidak ada Hard Error pada Preflight!")

    if warnings:
        print(f"\n⚠️ WARNINGS ({len(warnings)} peringatan):")
        for idx, w in enumerate(warnings, 1):
            print(f"  {idx}. {w}")

    # 2. Run Infeasibility Diagnosis
    print("\n--- 2. RUNNING INFEASIBILITY DIAGNOSIS ---")
    diag_recs = _diagnose_infeasibility(teachers, classes, allocations, ts_set, subjects_map)
    if diag_recs:
        print(f"\n❌ TEMUAN ANALISIS SOLVER ({len(diag_recs)} penyebab utama gagal generate):")
        for idx, r in enumerate(diag_recs, 1):
            print(f"  {idx}. [{r.get('type')}] {r.get('message')}")
    else:
        print("\n✅ Diagnosa awal tidak menemukan bentrok fatal.")

if __name__ == '__main__':
    main()
