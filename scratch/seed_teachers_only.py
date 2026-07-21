import pymysql
import sys

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import TEACHERS_BEKASI, TEACHERS_JAKARTA

def main():
    print("================ SEEDING TEACHERS ONLY ================")
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": ""
    }
    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    try:
        dbs = ["jadwal_bekasi", "jadwal_jakarta", "lms_db"]
        
        for db in dbs:
            print(f"\nSeeding teachers in database: {db}...")
            cur.execute(f"USE {db}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE teachers;")
            
            # Select appropriate teachers list
            teachers_list = TEACHERS_JAKARTA if "jakarta" in db.lower() else TEACHERS_BEKASI
            
            for t in teachers_list:
                cur.execute("""
                    INSERT INTO teachers 
                    (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang,
                     hari_tersedia_pagi, hari_tersedia_siang, no_wa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    t["kode_guru"],
                    t["nama_guru"],
                    t["hari_tersedia"],
                    t["shift_pagi"],
                    t["shift_siang"],
                    t["hari_tersedia_pagi"],
                    t["hari_tersedia_siang"],
                    t["no_wa"]
                ))
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print(f"  -> Successfully seeded {len(teachers_list)} teachers.")
            
        print("\nAll databases have their teachers table seeded successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR seeding teachers: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
