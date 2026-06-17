import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def check_coverage():
    conn = get_db_connection()
    try:
        classes = db_fetchall(conn, "SELECT * FROM classes")
        teachers = db_fetchall(conn, "SELECT * FROM teachers")
        
        pagi_classes = [c for c in classes if c['shift_operasional'] == 'PAGI']
        siang_classes = [c for c in classes if c['shift_operasional'] == 'SIANG']
        
        n_pagi = len(pagi_classes)
        n_siang = len(siang_classes)
        
        DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
        
        print(f"PAGI classes: {n_pagi}")
        print(f"SIANG classes: {n_siang}\n")
        
        print("=== DAILY COVERAGE ANALYSIS ===")
        for day in DAYS:
            pagi_teachers = []
            siang_teachers = []
            for t in teachers:
                hari_pagi = json.loads(t["hari_tersedia_pagi"] or "[]")
                hari_siang = json.loads(t["hari_tersedia_siang"] or "[]")
                
                if t["shift_pagi"] and day in hari_pagi:
                    pagi_teachers.append(t["nama_guru"])
                if t["shift_siang"] and day in hari_siang:
                    siang_teachers.append(t["nama_guru"])
            
            print(f"{day}:")
            print(f"  PAGI: {len(pagi_teachers)} teachers vs {n_pagi} classes")
            if len(pagi_teachers) < n_pagi:
                print(f"    ⚠️ WARNING: Deficit of {n_pagi - len(pagi_teachers)} teachers!")
            print(f"  SIANG: {len(siang_teachers)} teachers vs {n_siang} classes")
            if len(siang_teachers) < n_siang:
                print(f"    ⚠️ WARNING: Deficit of {n_siang - len(siang_teachers)} teachers!")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check_coverage()
