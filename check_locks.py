import sys
from dotenv import load_dotenv
sys.path.insert(0, 'd:/Jadwal')
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
try:
    cur.execute("""
        SELECT l.pid, mode, granted, query, state
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        WHERE relation::regclass::text IN ('teachers', 'classes', 'subjects', 'teacher_subjects', 'class_subjects', 'timetable');
    """)
    rows = cur.fetchall()
    print("Active locks on SITAB tables:")
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)
finally:
    cur.close()
    conn.close()
