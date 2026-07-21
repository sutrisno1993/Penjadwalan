import urllib.request
import json

base_url = "http://127.0.0.1:8002"
endpoints = [
    "/api/stats",
    "/api/teachers",
    "/api/subjects",
    "/api/classes",
    "/api/teacher-subjects",
    "/api/class-subjects",
    "/api/timetable",
    "/api/lms-endpoints",
    "/api/health-check",
    "/api/guru-mutlak"
]

print("=== TESTING ALL API ENDPOINTS (Default Branch) ===")
for ep in endpoints:
    try:
        req = urllib.request.Request(base_url + ep, headers={"X-Branch": "bekasi"})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            count = len(data) if isinstance(data, list) else (len(data.keys()) if isinstance(data, dict) else "N/A")
            print(f"  - {ep}: HTTP {res.status} | Data: {count} items/keys")
    except Exception as e:
        print(f"  - {ep}: ERROR {e}")
