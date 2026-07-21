import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection

load_dotenv()

conn = get_db_connection()
cur = conn.cursor()
try:
    # Update Luthfi: remove SENIN from hari_tersedia_pagi and hari_tersedia_siang
    hari_pagi = ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
    hari_siang = ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
    
    cur.execute("""
        UPDATE teachers 
        SET hari_tersedia_pagi = %s, 
            hari_tersedia_siang = %s,
            hari_tersedia = %s,
            min_jp = NULL,
            max_jp = NULL
        WHERE kode_guru = 13
    """, (json.dumps(hari_pagi), json.dumps(hari_siang), json.dumps(hari_pagi)))
    
    conn.commit()
    print("Berhasil mengatur hari Luthfi menjadi SELASA-SABTU (menghilangkan SENIN)")
    print("   min_jp dan max_jp di-set NULL")
finally:
    cur.close()
    conn.close()
