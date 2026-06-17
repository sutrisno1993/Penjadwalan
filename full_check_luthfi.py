import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchone

load_dotenv()
conn = get_db_connection()
try:
    luthfi = db_fetchone(conn, "SELECT * FROM teachers WHERE nama_guru LIKE %s", ('%LUTHFI%',))
    print('--- FULL DATA LUTHFI ---')
    for k, v in luthfi.items():
        print(f'{k}: {v}')
finally:
    conn.close()
