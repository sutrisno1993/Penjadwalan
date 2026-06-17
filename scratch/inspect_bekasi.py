import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch, db_fetchall

def main():
    active_branch.set("bekasi")
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, max_jp FROM teachers ORDER BY nama_guru")
        classes = db_fetchall(conn, "SELECT id_kelas, nama_kelas, shift_operasional FROM classes ORDER BY nama_kelas")
        subjects = db_fetchall(conn, "SELECT id_mapel, nama_mapel, kategori_mapel FROM subjects ORDER BY nama_mapel")
        allocations = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
                   c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
        """)
        ts = db_fetchall(conn, "SELECT id_guru, id_mapel FROM teacher_subjects")
        
        print("--- BEKASI DATABASE INSPECTION ---")
        print(f"Teachers count: {len(teachers)}")
        print(f"Classes count: {len(classes)}")
        print(f"Subjects count: {len(subjects)}")
        print(f"Allocations count: {len(allocations)}")
        print(f"Teacher qualifications count: {len(ts)}")
        
        print("\n--- ALLOCATIONS DETAILED ---")
        for a in allocations:
            fixed_str = f"LOCKED to {a['id_guru_mutlak']}" if a['id_guru_mutlak'] else "pool"
            print(f"  ClassSubject ID {a['id_class_subject']}: {a['nama_kelas']} - {a['nama_mapel']} ({a['durasi_jp']} JP, {fixed_str})")
            
        print("\n--- TEACHERS DETAILED ---")
        for t in teachers:
            quals = [a['nama_mapel'] for a in subjects if (t['id_guru'], a['id_mapel']) in {(row['id_guru'], row['id_mapel']) for row in ts}]
            print(f"  Teacher {t['nama_guru']} (ID {t['id_guru']}, Code {t['kode_guru']}): Shift Pagi={t['shift_pagi']}, Siang={t['shift_siang']}, Max JP={t['max_jp']}. Quals: {', '.join(quals)}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    main()
