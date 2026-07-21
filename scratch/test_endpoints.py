import urllib.request
import json

endpoints = [
    '/api/teachers',
    '/api/classes',
    '/api/subjects',
    '/api/class-subjects',
    '/api/teacher-subjects',
    '/api/time-slots',
    '/api/guru-mutlak',
    '/api/guru-4jp-restrictions',
    '/api/ketersediaan-hari',
    '/api/feasibility-matrix',
    '/api/lms-endpoints'
]

print("=== TESTING ALL API ENDPOINTS ON http://127.0.0.1:8002 ===")
for ep in endpoints:
    url = f"http://127.0.0.1:8002{ep}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[OK] {ep} -> Status {resp.status}, Items/Keys: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
    except Exception as e:
        print(f"[FAIL] {ep} -> Error: {e}")
