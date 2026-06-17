import sys
import json
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch, db_fetchall

def main():
    active_branch.set("bekasi")
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT * FROM teachers")
        classes = db_fetchall(conn, "SELECT * FROM classes")
        allocations = db_fetchall(conn, """
            SELECT cs.*, c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
        """)
        
        teachers_map = {t["id_guru"]: t for t in teachers}
        for t in teachers:
            t["hari_tersedia_pagi"] = json.loads(t["hari_tersedia_pagi"] or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            
        print("=== DETIL ALOKASI TERKUNCI PER GURU ===")
        for t in teachers:
            tid = t["id_guru"]
            t_allocs = [a for a in allocations if a["id_guru_mutlak"] == tid]
            if not t_allocs:
                continue
            
            print(f"\nGuru: {t['nama_guru']} (ID {tid}, Max JP {t['max_jp']})")
            pagi_allocs = [a for a in t_allocs if a["shift_operasional"] == "PAGI"]
            siang_allocs = [a for a in t_allocs if a["shift_operasional"] == "SIANG"]
            
            pagi_jp = sum(a["durasi_jp"] for a in pagi_allocs)
            siang_jp = sum(a["durasi_jp"] for a in siang_allocs)
            
            print(f"  PAGI: {pagi_jp} JP")
            for a in pagi_allocs:
                print(f"    - {a['nama_kelas']} | {a['nama_mapel']} ({a['durasi_jp']} JP)")
            print(f"  SIANG: {siang_jp} JP")
            for a in siang_allocs:
                print(f"    - {a['nama_kelas']} | {a['nama_mapel']} ({a['durasi_jp']} JP)")
                
    finally:
        conn.close()

if __name__ == "__main__":
    main()
