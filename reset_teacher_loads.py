import os
from dotenv import load_dotenv
from backend.database import get_db_connection

load_dotenv()
conn = get_db_connection()
try:
    cur = conn.cursor()
    # Ubah semua min_jp dan max_jp menjadi NULL untuk testing
    cur.execute("UPDATE teachers SET min_jp = NULL, max_jp = NULL")
    conn.commit()
    print("Berhasil reset min_jp dan max_jp menjadi NULL untuk semua guru.")
finally:
    conn.close()
