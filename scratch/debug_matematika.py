import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection

def main():
    conn = get_db_connection(branch="jakarta")
    c = conn.cursor()
    c.execute("""
        SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak, t.nama_guru 
        FROM class_subjects cs 
        JOIN classes c ON cs.id_kelas=c.id_kelas 
        JOIN subjects s ON cs.id_mapel=s.id_mapel 
        LEFT JOIN teachers t ON cs.id_guru_mutlak=t.id_guru 
        WHERE c.nama_kelas='X AKL 1'
    """)
    rows = c.fetchall()
    print(f"Total rows for X AKL 1: {len(rows)}")
    for r in rows:
        print(r)

if __name__ == '__main__':
    main()
