import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall

def main():
    conn = get_db_connection()
    try:
        print("=== BEKASI ALLOCATIONS WITH FIXED TEACHER ===")
        rows = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.durasi_jp, cs.id_guru_mutlak, 
                   c.nama_kelas, s.nama_mapel, t.nama_guru
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            JOIN teachers t ON cs.id_guru_mutlak = t.id_guru
            ORDER BY t.nama_guru
        """)
        print(f"Total locked allocations: {len(rows)}")
        for r in rows:
            print(f"  Teacher: {r['nama_guru']} (ID: {r['id_guru_mutlak']}) | Class: {r['nama_kelas']} | Mapel: {r['nama_mapel']} | JP: {r['durasi_jp']}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
