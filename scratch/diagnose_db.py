import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def run_diagnostics():
    conn = get_db_connection()
    try:
        # 1. Check classes and their shift demand
        classes = db_fetchall(conn, "SELECT * FROM classes")
        print(f"Total Kelas: {len(classes)}")
        pagi_classes = [c for c in classes if c['shift_operasional'] == 'PAGI']
        siang_classes = [c for c in classes if c['shift_operasional'] == 'SIANG']
        print(f"  - PAGI: {len(pagi_classes)} kelas")
        print(f"  - SIANG: {len(siang_classes)} kelas")
        
        # 2. Check total JP demand
        allocations = db_fetchall(conn, """
            SELECT cs.*, c.shift_operasional, c.nama_kelas, s.nama_mapel, s.kategori_mapel
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
        """)
        
        total_jp_pagi = sum(a['durasi_jp'] for a in allocations if a['shift_operasional'] == 'PAGI')
        total_jp_siang = sum(a['durasi_jp'] for a in allocations if a['shift_operasional'] == 'SIANG')
        print(f"Total JP Demand:")
        print(f"  - PAGI: {total_jp_pagi} JP (Max possible: {len(pagi_classes) * 40} JP)")
        print(f"  - SIANG: {total_jp_siang} JP (Max possible: {len(siang_classes) * 40} JP)")
        
        # 3. Check for locked teachers
        locked = [a for a in allocations if a['id_guru_mutlak'] is not None]
        print(f"Locked Teachers Allocations count: {len(locked)}")
        if locked:
            for l in locked:
                print(f"  - Kelas: {l['nama_kelas']}, Mapel: {l['nama_mapel']}, Guru Mutlak ID: {l['id_guru_mutlak']}, Durasi: {l['durasi_jp']}")

        # 4. Check teachers and their shift/day availability
        teachers = db_fetchall(conn, "SELECT * FROM teachers")
        print(f"Total Teachers: {len(teachers)}")
        
        # Check active teachers and their available hours
        DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
        SHIFT_LIMITS = {
            "PAGI":  {"SENIN": 6, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 7},
            "SIANG": {"SENIN": 7, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 6},
        }
        
        total_capacity_pagi = 0
        total_capacity_siang = 0
        
        for t in teachers:
            t["hari_tersedia_pagi"] = (json.loads(t["hari_tersedia_pagi"]) if t.get("hari_tersedia_pagi") else [])
            t["hari_tersedia_siang"] = (json.loads(t["hari_tersedia_siang"]) if t.get("hari_tersedia_siang") else [])
            
            # Max JP capacity for this teacher in PAGI shift
            if t['shift_pagi']:
                slots_pagi = sum(SHIFT_LIMITS["PAGI"][d] for d in t["hari_tersedia_pagi"])
                max_jp = t['max_jp'] if t['max_jp'] is not None else 60
                total_capacity_pagi += min(slots_pagi, max_jp)
                
            if t['shift_siang']:
                slots_siang = sum(SHIFT_LIMITS["SIANG"][d] for d in t["hari_tersedia_siang"])
                max_jp = t['max_jp'] if t['max_jp'] is not None else 60
                total_capacity_siang += min(slots_siang, max_jp)
                
        print(f"Total Teacher Capacity:")
        print(f"  - PAGI: {total_capacity_pagi} JP")
        print(f"  - SIANG: {total_capacity_siang} JP")

    finally:
        conn.close()

if __name__ == "__main__":
    run_diagnostics()
