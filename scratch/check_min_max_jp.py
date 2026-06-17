import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch, db_fetchall

def main():
    active_branch.set("bekasi")
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT nama_guru, min_jp, max_jp FROM teachers ORDER BY nama_guru")
        print("=== MIN & MAX JP BEKASI ===")
        for t in teachers:
            if t["min_jp"] is not None or t["max_jp"] is not None:
                print(f"  {t['nama_guru']}: min_jp={t['min_jp']}, max_jp={t['max_jp']}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
