import sys
import re
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import get_class_info

def parse_sql_classes(sql_path):
    class_names = set()
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([0-9]+|NULL)\s*,\s*([0-9]+)\s*\)"
    matches = re.findall(pattern, content)
    
    for match in matches:
        class_name = match[0].strip()
        class_names.add(class_name)
        
    return sorted(list(class_names))

def main():
    sql_path = "d:/Jadwal/backend/seed_class_subjects.sql"
    classes = parse_sql_classes(sql_path)
    print(f"Parsed {len(classes)} unique classes from SQL.")
    
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
            print(f"\nSeeding classes in database: {db}...")
            cur.execute(f"USE {db}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE classes;")
            
            for class_name in classes:
                tingkat, jurusan, shift = get_class_info(class_name)
                cur.execute("""
                    INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                    VALUES (%s, %s, %s, %s)
                """, (class_name, shift, tingkat, jurusan))
            
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print(f"  -> Successfully seeded {len(classes)} classes.")
            
        print("\nAll databases have their classes table seeded successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR seeding classes: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
