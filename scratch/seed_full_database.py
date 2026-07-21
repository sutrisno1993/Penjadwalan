import sys
import re
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import SUBJECTS, TEACHERS, TEACHER_SUBJECTS, get_class_info

FUZZY_SUBJECT_MAP = {
    "Pendidikan Agama dan Budi Pekerti": "Pendidikan Agama Islam",
    "Pendidikan Pancasila dan Kewarganegaraan": "PPKn",
    "Pendidikan Jasmani, Olah Raga & Kesehatan": "Penjasorkes",
    "Teknologi Infrastruktur Jaringan": "Teknik Infrastruktur Jaringan",
    "Teknologi Layanan Jaringan": "Tek Layanan Jaringan",
    "Administrasi Sistem Jaringan": "Adm Sistem Jaringan"
}

def parse_sql_allocations(sql_path):
    allocations = []
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([0-9]+|NULL)\s*,\s*([0-9]+)\s*\)"
    matches = re.findall(pattern, content)
    
    for match in matches:
        class_name = match[0].strip()
        subject_name = match[1].strip()
        
        # Apply fuzzy mapping
        if subject_name in FUZZY_SUBJECT_MAP:
            subject_name = FUZZY_SUBJECT_MAP[subject_name]
            
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
    allocations = parse_sql_allocations(sql_path)
    print(f"Parsed {len(allocations)} allocations from SQL.")
    
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
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # Step 1: Seed subjects
            cur.execute("TRUNCATE TABLE subjects;")
            for s in SUBJECTS:
                cur.execute("""
                    INSERT IGNORE INTO subjects (nama_mapel, kategori_mapel)
                    VALUES (%s, %s)
                """, (s["nama_mapel"], s["kategori_mapel"]))
            print(f"  -> Seeded {len(SUBJECTS)} subjects.")
            
            # Build lookups
            cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
            subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
            
            cur.execute("SELECT id_guru, kode_guru FROM teachers")
            teacher_map = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}
            
            # Step 2: Seed teacher_subjects (qualifications)
            cur.execute("TRUNCATE TABLE teacher_subjects;")
            for kode_guru, mapel_list in TEACHER_SUBJECTS.items():
                id_guru = teacher_map.get(kode_guru)
                if not id_guru:
                    continue
                for nama_mapel in mapel_list:
                    id_mapel = subject_map.get(nama_mapel)
                    if id_mapel:
                        cur.execute("""
                            INSERT IGNORE INTO teacher_subjects (id_guru, id_mapel)
                            VALUES (%s, %s)
                        """, (id_guru, id_mapel))
            print("  -> Seeded teacher_subjects relations.")
            
            # Step 3: Seed classes dynamically from allocations
            cur.execute("TRUNCATE TABLE class_subjects;")
            cur.execute("TRUNCATE TABLE classes;")
            unique_classes = sorted(list({a["class"] for a in allocations}))
            class_map = {}
            for class_name in unique_classes:
                tingkat, jurusan, shift = get_class_info(class_name)
                cur.execute("""
                    INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                    VALUES (%s, %s, %s, %s)
                """, (class_name, shift, tingkat, jurusan))
                class_map[class_name] = cur.lastrowid
            print(f"  -> Seeded {len(unique_classes)} classes.")
            
            # Step 4: Seed allocations from seed_class_subjects.sql
            inserted = 0
            skipped = 0
            for a in allocations:
                id_kelas = class_map.get(a["class"])
                id_mapel = subject_map.get(a["subject"])
                
                if not id_kelas or not id_mapel:
                    print(f"  [WARN] Skipping: class={a['class']}, subject={a['subject']}")
                    skipped += 1
                    continue
                    
                id_guru_mutlak = None
                if a["teacher_code"] is not None:
                    id_guru_mutlak = teacher_map.get(a["teacher_code"])
                
                cur.execute("""
                    INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        durasi_jp = VALUES(durasi_jp),
                        id_guru_mutlak = VALUES(id_guru_mutlak)
                """, (id_kelas, id_mapel, a["durasi_jp"], id_guru_mutlak))
                inserted += 1
                
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print(f"  -> Seeded {inserted} allocations successfully. Skipped {skipped}.")
            
        print("\nAll databases fully populated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
