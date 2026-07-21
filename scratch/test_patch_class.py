import requests
import json

def test():
    # Find the class id for 'X TSM 2' first
    try:
        r = requests.get("http://127.0.0.1:8002/api/classes?branch=bekasi")
        classes = r.json()
        target_id = None
        for c in classes:
            if c["nama_kelas"] == "X TSM 2":
                target_id = c["id_kelas"]
                break
        
        if target_id is None:
            print("Class 'X TSM 2' not found!")
            return
            
        print(f"Testing PATCH on class '{c['nama_kelas']}' with ID: {target_id}...")
        
        body = {
            "nama_kelas": "X TSM 2",
            "shift_operasional": "SIANG",
            "tingkat": "X",
            "jurusan": "TSM"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Branch": "bekasi"
        }
        
        response = requests.patch(f"http://127.0.0.1:8002/api/classes/{target_id}", json=body, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"Connection/execution error: {e}")

if __name__ == '__main__':
    test()
