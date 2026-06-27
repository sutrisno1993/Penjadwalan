import requests

BASE_URL = "http://localhost:8001/api"
headers = {"X-Branch": "bekasi"}

def verify():
    print("Fetching teachers...")
    res = requests.get(f"{BASE_URL}/teachers", headers=headers)
    assert res.status_code == 200
    teachers = res.json()
    print(f"Total teachers: {len(teachers)}")
    
    # Try adding a test teacher with no_wa
    test_teacher = {
        "nama_guru": "Test WA Guru",
        "kode_guru": 9999,
        "hari_tersedia": ["SENIN", "SELASA"],
        "shift_pagi": True,
        "shift_siang": False,
        "hari_tersedia_pagi": ["SENIN", "SELASA"],
        "hari_tersedia_siang": [],
        "min_jp": 2,
        "max_jp": 30,
        "no_wa": "087777777777"
    }
    
    print("Creating test teacher...")
    res_create = requests.post(f"{BASE_URL}/teachers", json=test_teacher, headers=headers)
    if res_create.status_code != 200:
        print(f"Failed to create: {res_create.text}")
        return
    
    created = res_create.json()
    print(f"Created teacher ID: {created.get('id_guru')}")
    
    # Fetch teachers again
    res = requests.get(f"{BASE_URL}/teachers", headers=headers)
    teachers = res.json()
    found = [t for t in teachers if t["kode_guru"] == 9999]
    assert len(found) > 0, "Test teacher not found!"
    assert found[0]["no_wa"] == "087777777777", f"no_wa mismatch! Found: {found[0]['no_wa']}"
    print("Successfully verified: no_wa field created and retrieved correctly!")
    
    # Clean up
    teacher_id = found[0]["id_guru"]
    print(f"Deleting test teacher {teacher_id}...")
    res_del = requests.delete(f"{BASE_URL}/teachers/{teacher_id}", headers=headers)
    assert res_del.status_code == 200
    print("Cleanup successful.")

if __name__ == "__main__":
    verify()
