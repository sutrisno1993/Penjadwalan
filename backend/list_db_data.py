import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def dump_data():
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru FROM teachers ORDER BY kode_guru")
        classes = db_fetchall(conn, "SELECT id_kelas, nama_kelas, shift_operasional FROM classes ORDER BY nama_kelas")
        subjects = db_fetchall(conn, "SELECT id_mapel, nama_mapel, kategori_mapel FROM subjects ORDER BY nama_mapel")
        
        data = {
            "teachers": teachers,
            "classes": classes,
            "subjects": subjects
        }
        
        with open("backend/db_dump.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        print("Successfully dumped database data to backend/db_dump.json")
    finally:
        conn.close()

if __name__ == "__main__":
    dump_data()
