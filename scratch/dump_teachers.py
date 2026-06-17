import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def dump_teachers():
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, hari_tersedia, hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp FROM teachers ORDER BY id_guru")
        print("=== DATA GURU ===")
        for t in teachers:
            t["hari_tersedia"] = json.loads(t["hari_tersedia"] or "[]")
            t["hari_tersedia_pagi"] = json.loads(t["hari_tersedia_pagi"] or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            print(f"ID: {t['id_guru']}, Kode: {t['kode_guru']}, Nama: {t['nama_guru']}")
            print(f"  Pagi: {t['shift_pagi']} {t['hari_tersedia_pagi']}")
            print(f"  Siang: {t['shift_siang']} {t['hari_tersedia_siang']}")
            print(f"  Min/Max JP: {t['min_jp']}/{t['max_jp']}")
    finally:
        conn.close()

if __name__ == "__main__":
    dump_teachers()
