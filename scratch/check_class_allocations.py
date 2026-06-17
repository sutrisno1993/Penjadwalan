import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def check_allocations():
    conn = get_db_connection()
    try:
        # Get id of XI AK 1
        row = db_fetchall(conn, "SELECT id_kelas, nama_kelas, shift_operasional FROM classes WHERE nama_kelas = 'XI AK 1'")
        if not row:
            print("Class XI AK 1 not found!")
            return
        cid = row[0]['id_kelas']
        
        print(f"=== ALLOCATIONS FOR XI AK 1 (ID: {cid}, Shift: {row[0]['shift_operasional']}) ===")
        allocs = db_fetchall(conn, """
            SELECT cs.id_class_subject, s.nama_mapel, s.kategori_mapel, cs.durasi_jp, cs.id_guru_mutlak, g.nama_guru
            FROM class_subjects cs
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            LEFT JOIN teachers g ON cs.id_guru_mutlak = g.id_guru
            WHERE cs.id_kelas = %s
        """, (cid,))
        
        total_jp = 0
        for a in allocs:
            print(f"Mapel: {a['nama_mapel']} ({a['kategori_mapel']}) | JP: {a['durasi_jp']} | Locked Teacher: {a['nama_guru'] or '-'}")
            total_jp += a['durasi_jp']
        print(f"Total JP for XI AK 1: {total_jp} JP")
        
        # Who are the qualified teachers for each mapel?
        print("\n=== QUALIFIED TEACHERS PER MAPEL FOR XI AK 1 ===")
        for a in allocs:
            teachers = db_fetchall(conn, """
                SELECT t.id_guru, t.nama_guru, t.shift_pagi, t.shift_siang, t.hari_tersedia_siang
                FROM teacher_subjects ts
                JOIN teachers t ON ts.id_guru = t.id_guru
                WHERE ts.id_mapel = (SELECT id_mapel FROM subjects WHERE nama_mapel = %s)
            """, (a['nama_mapel'],))
            print(f"\nMapel: {a['nama_mapel']}")
            for t in teachers:
                print(f"  - {t['nama_guru']} (Siang: {t['shift_siang']} {t['hari_tersedia_siang']})")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check_allocations()
