import re
import os
import sys
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import get_class_info

def parse_sql_allocations(sql_path):
    allocations = []
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to match VALUES tuples: ('class', 'subject', teacher_code, durasi_jp)
    pattern = r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([0-9]+|NULL)\s*,\s*([0-9]+)\s*\)"
    matches = re.findall(pattern, content)
    
    for match in matches:
        class_name = match[0].strip()
        subject_name = match[1].strip()
        teacher_code = None if match[2] == 'NULL' else int(match[2])
        durasi_jp = int(match[3])
        
        allocations.append({
            "class": class_name,
            "subject": subject_name,
            "teacher_code": teacher_code,
            "durasi_jp": durasi_jp
        })
        
    return allocations

def main():
    sql_path = "d:/Jadwal/backend/seed_class_subjects.sql"
    if not os.path.exists(sql_path):
        print(f"File SQL tidak ditemukan: {sql_path}")
        return
        
    allocations = parse_sql_allocations(sql_path)
    print(f"Parsed {len(allocations)} allocations from SQL.")
    if not allocations:
        return
        
    # Check first 5
    for i, a in enumerate(allocations[:5]):
        print(f"Sample {i+1}: {a}")
        
    # Connect to databases
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": ""
    }
    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        dbs = ["jadwal_bekasi", "jadwal_jakarta", "lms_db"]
        
        for db in dbs:
            print(f"\n================ DATABASE: {db} ================")
            cur.execute(f"USE {db}")
            
            # Disable foreign key checks and clean class_subjects + classes
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE class_subjects;")
            cur.execute("TRUNCATE TABLE classes;")
            
            # Build lookups
            # Get subjects lookup
            cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
            subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
            
            # Get teachers lookup
            cur.execute("SELECT id_guru, kode_guru FROM teachers")
            teacher_map = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}
            
            # Insert classes dynamically
            unique_classes = sorted(list({a["class"] for a in allocations}))
            class_map = {}
            for class_name in unique_classes:
                tingkat, jurusan, shift = get_class_info(class_name)
                cur.execute("""
                    INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                    VALUES (%s, %s, %s, %s)
                """, (class_name, shift, tingkat, jurusan))
                class_map[class_name] = cur.lastrowid
                
            print(f"  -> Inserted {len(unique_classes)} classes.")
            
            # Insert allocations
            inserted = 0
            skipped = 0
            for a in allocations:
                id_kelas = class_map.get(a["class"])
                id_mapel = subject_map.get(a["subject"])
                
                if not id_kelas or not id_mapel:
                    # Try fuzzy mapping or print warning
                    print(f"  [WARN] Skipping allocation because class '{a['class']}' or subject '{a['subject']}' not found in DB.")
                    skipped += 1
                    continue
                    
                id_guru_mutlak = None
                if a["teacher_code"] is not None:
                    id_guru_mutlak = teacher_map.get(a["teacher_code"])
                    if not id_guru_mutlak:
                        print(f"  [WARN] Teacher with code {a['teacher_code']} not found in DB.")
                
                cur.execute("""
                    INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak)
                    VALUES (%s, %s, %s, %s)
                """, (id_kelas, id_mapel, a["durasi_jp"], id_guru_mutlak))
                inserted += 1
                
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print(f"  -> Seeded {inserted} allocations successfully. Skipped {skipped}.")
            
        print("\nAll databases populated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR seeding: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
