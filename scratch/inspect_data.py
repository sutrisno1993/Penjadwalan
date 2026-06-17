import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall, active_branch
import json

def main():
    conn = get_db_connection()
    try:
        astri = db_fetchall(conn, "SELECT * FROM teachers WHERE nama_guru LIKE %s", ('%ASTRI%',))
        if astri:
            t = astri[0]
            print("Teacher:", t['nama_guru'])
            print("  shift_pagi:", t['shift_pagi'])
            print("  shift_siang:", t['shift_siang'])
            print("  hari_tersedia:", t['hari_tersedia'])
            print("  hari_tersedia_pagi:", t['hari_tersedia_pagi'])
            print("  hari_tersedia_siang:", t['hari_tersedia_siang'])
            print("  allowed_jp_pagi:", t['allowed_jp_pagi'])
            print("  allowed_jp_siang:", t['allowed_jp_siang'])
        else:
            print("Astri Wulandari not found!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
