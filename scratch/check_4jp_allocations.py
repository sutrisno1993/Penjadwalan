import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall

def check():
    conn = get_db_connection()
    try:
        allocs = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, c.nama_kelas, cs.id_mapel, m.nama_mapel, cs.durasi_jp
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects m ON cs.id_mapel = m.id_mapel
            WHERE cs.durasi_jp >= 4
            ORDER BY cs.durasi_jp DESC, c.nama_kelas
        """)
        print(f"Ditemukan {len(allocs)} alokasi dengan durasi >= 4 JP:")
        for a in allocs:
            print(f"- Kelas: {a['nama_kelas']:<10} | Mapel: {a['nama_mapel']:<30} | Durasi: {a['durasi_jp']} JP")
    finally:
        conn.close()

if __name__ == '__main__':
    check()
