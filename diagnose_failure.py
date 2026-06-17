import logging
from backend.solver import generate_timetable
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

print("Mulai menjalankan generator untuk diagnosa...")
res = generate_timetable()
print("\n--- HASIL DIAGNOSA ---")
print(f"Status: {res['status']}")
if res.get('errors'):
    print(f"Errors: {res['errors']}")
if res.get('warnings'):
    print("Warnings (mungkin menunjukkan bottleneck):")
    for w in res['warnings'][:10]:
        print(f"  - {w}")
