import sys
from dotenv import load_dotenv
sys.path.insert(0, 'd:/Jadwal')
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection

print("Connecting to database...")
conn = get_db_connection()
conn.autocommit = True
cur = conn.cursor()
print("Terminating other backends to release locks...")
try:
    cur.execute("""
        SELECT pg_terminate_backend(pid), query, state
        FROM pg_stat_activity
        WHERE pid <> pg_backend_pid()
          AND datname = 'postgres';
    """)
    rows = cur.fetchall()
    print(f"Terminated {len(rows)} connections:")
    for r in rows:
        print(f"  - PID {r[0]}: {r[1]} ({r[2]})")
except Exception as e:
    print("Error:", e)
finally:
    cur.close()
    conn.close()
print("Done!")
