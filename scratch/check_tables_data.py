import sys
sys.path.insert(0, '.')
import backend.database as db

conn = db.get_db_connection()
cur = conn.cursor()

tables = ['lms_endpoints', 'system_settings', 'time_slots', 'teachers', 'class_subjects']
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) as c FROM `{t}`;")
        row = cur.fetchone()
        print(f"Table '{t}': {row['c']} rows")
    except Exception as e:
        print(f"Table '{t}': Error {e}")

cur.close()
conn.close()
