import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection

def main():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id_guru, kode_guru, nama_guru FROM teachers WHERE nama_guru LIKE '%NAAFI%' OR kode_guru IN (17, 18)")
    print("Teachers:", c.fetchall())

    c.execute("""
        SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak, t.nama_guru, t.kode_guru
        FROM class_subjects cs 
        JOIN classes c ON cs.id_kelas=c.id_kelas 
        JOIN subjects s ON cs.id_mapel=s.id_mapel 
        LEFT JOIN teachers t ON cs.id_guru_mutlak=t.id_guru 
        WHERE c.nama_kelas='X AKL 1'
    """)
    print("\nClass subjects for X AKL 1:")
    for r in c.fetchall():
        print(r)

if __name__ == '__main__':
    main()
