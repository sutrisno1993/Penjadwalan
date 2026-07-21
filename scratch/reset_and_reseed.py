import pymysql
import sys
import os

# Insert workspace root to sys.path so we can import backend packages
sys.path.insert(0, 'd:/Jadwal')

from backend.database import active_branch
from backend.seeder import run_seeder

def main():
    print("================ RESETTING AND SEEDING DATABASES ==================")
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": ""
    }
    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Step 1: Truncate tables in jadwal_bekasi, jadwal_jakarta, and lms_db
        dbs = ["jadwal_bekasi", "jadwal_jakarta", "lms_db"]
        tables_to_truncate = ["timetable", "class_subjects", "teacher_subjects", "teachers", "classes", "subjects"]
        
        for db in dbs:
            print(f"Truncating master tables in: {db}...")
            cur.execute(f"USE {db}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table in tables_to_truncate:
                cur.execute(f"TRUNCATE TABLE {table};")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            
        print("All database tables truncated successfully.")
        
        # Step 2: Seed jadwal_bekasi and jadwal_jakarta using seeder.py
        print("\nSeeding jadwal_bekasi from scratch...")
        token = active_branch.set("bekasi")
        run_seeder()
        active_branch.reset(token)
        
        print("\nSeeding jadwal_jakarta from scratch...")
        token = active_branch.set("jakarta")
        run_seeder()
        active_branch.reset(token)
        
        # Step 3: Copy seeded data from jadwal_bekasi to lms_db
        print("\nCopying master data from jadwal_bekasi to lms_db...")
        
        # Helper to copy table
        def copy_table(table_name, columns):
            col_list = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            cur.execute(f"SELECT {col_list} FROM jadwal_bekasi.{table_name}")
            rows = cur.fetchall()
            
            print(f"  -> Copying {len(rows)} rows for table '{table_name}'...")
            
            cur.execute(f"USE lms_db")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for row in rows:
                values = [row[col] for col in columns]
                cur.execute(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})", tuple(values))
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            
        # Copy tables
        copy_table("teachers", [
            "id_guru", "nama_guru", "kode_guru", "hari_tersedia", 
            "shift_pagi", "shift_siang", "hari_tersedia_pagi", "hari_tersedia_siang", "no_wa"
        ])
        copy_table("classes", ["id_kelas", "nama_kelas", "shift_operasional", "tingkat", "jurusan"])
        copy_table("subjects", ["id_mapel", "nama_mapel", "kategori_mapel", "tingkat", "jurusan"])
        copy_table("class_subjects", ["id_class_subject", "id_kelas", "id_mapel", "durasi_jp", "id_guru_mutlak"])
        copy_table("teacher_subjects", ["id_teacher_subject", "id_guru", "id_mapel"])
        
        print("\nAll databases are clean and seeded successfully!")
        
    except Exception as e:
        print(f"\nERROR running reset and seed: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
