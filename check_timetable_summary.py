import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()
conn = get_db_connection()
try:
    rows = db_fetchall(conn, "SELECT t.id_guru, g.nama_guru, COUNT(*) as n FROM timetable t JOIN teachers g ON t.id_guru = g.id_guru GROUP BY t.id_guru, g.nama_guru")
    print('--- RINGKASAN TIMETABLE ---')
    for r in rows:
        print(r)
finally:
    conn.close()
