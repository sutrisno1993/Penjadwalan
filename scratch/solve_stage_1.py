from backend.solver import _fetch_master_data, _run_solver, STAGE_FULL_QUAL
from dotenv import load_dotenv

def main():
    load_dotenv()
    teachers, classes, subjects_map, allocations, ts_set = _fetch_master_data()
    
    print("Running Stage 1 solve with 180 seconds limit...")
    res = _run_solver(teachers, classes, allocations, ts_set, subjects_map,
                      stage=STAGE_FULL_QUAL, time_limit=180.0)
    
    if res:
        print("\n=== SOLVE SUCCESSFUL ===")
        print(f"Status: {res['status']}")
        print(f"Fill percentage: {res['fill_percentage']}%")
        print(f"Warnings: {len(res['warnings'])}")
    else:
        print("\n=== SOLVE FAILED ===")
        print("Model is INFEASIBLE or timed out after 180 seconds.")

if __name__ == '__main__':
    main()
