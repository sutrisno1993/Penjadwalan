import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

print("Starting startup test...")
try:
    import backend.main
    print("SUCCESS")
except Exception as e:
    import traceback
    print("ERROR:", e)
    traceback.print_exc()
