import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall

def main():
    conn = get_db_connection()
    try:
        print("PUBLIC TIMETABLE COLUMNS:")
        for r in db_fetchall(conn, "SELECT column_name, data_type, ordinal_position FROM information_schema.columns WHERE table_name = 'timetable' AND table_schema = 'public' ORDER BY ordinal_position"):
            print(r)
            
        print("\nBEKASI TIMETABLE COLUMNS:")
        for r in db_fetchall(conn, "SELECT column_name, data_type, ordinal_position FROM information_schema.columns WHERE table_name = 'timetable' AND table_schema = 'bekasi' ORDER BY ordinal_position"):
            print(r)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
