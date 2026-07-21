import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.solver import generate_timetable

def main():
    print("--- CALLING GENERATE_TIMETABLE() DIRECTLY ---")
    res = generate_timetable()
    
    print("\nRESULT STATUS:", res.get("status"))
    if res.get("errors"):
        print("\n❌ ERRORS:")
        for err in res["errors"]:
            print(f"  - {err}")
            
    if res.get("warnings"):
        print(f"\n⚠️ WARNINGS ({len(res['warnings'])}):")
        for w in res["warnings"][:10]:
            print(f"  - {w}")

    if res.get("status") == "SUCCESS":
        print(f"\n✅ GENERATE SUKSES! Fill Pct: {res.get('fill_percentage')}%, Stage: {res.get('stage')}")
    else:
        print("\n❌ GENERATE GAGAL!")

if __name__ == '__main__':
    main()
