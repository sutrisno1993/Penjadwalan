import sys
sys.path.insert(0, 'd:/Jadwal')
from backend.solver import _fetch_master_data, _diagnose_infeasibility, _preflight
from dotenv import load_dotenv

def main():
    load_dotenv('d:/Jadwal/.env')
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    
    print("=== PREFLIGHT CHECK ===")
    errors, warnings = _preflight(teachers, classes, allocations, ts_set, subjects_map)
    print("Errors:")
    for e in errors:
        print(f"  - {e}")
    print("\nWarnings:")
    for w in warnings:
        print(f"  - {w}")
        
    print("\n=== INFEASIBILITY DIAGNOSTICS ===")
    diag_errors = _diagnose_infeasibility(teachers, classes, allocations, ts_set, subjects_map)
    if diag_errors:
        print("Infeasibility Errors found:")
        for de in diag_errors:
            print(f"  - {de}")
    else:
        print("No diagnostics errors detected by _diagnose_infeasibility. The bottleneck might be complex/interlocking constraints.")

if __name__ == '__main__':
    main()
