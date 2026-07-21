import sys
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import SUBJECTS, TEACHER_SUBJECTS

def main():
    print("================ SEEDING SUBJECTS ONLY ================")
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
            print(f"\nProcessing database: {db}...")
            cur.execute(f"USE {db}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # 1. Truncate and insert subjects
            cur.execute("TRUNCATE TABLE subjects;")
            for s in SUBJECTS:
                cur.execute("""
                    INSERT INTO subjects (nama_mapel, kategori_mapel)
                    VALUES (%s, %s)
                """, (s["nama_mapel"], s["kategori_mapel"]))
            print(f"  -> Seeded {len(SUBJECTS)} subjects successfully.")
            
            # Build lookups for teacher_subjects
            cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
            subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
            
            cur.execute("SELECT id_guru, kode_guru FROM teachers")
            teacher_map = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}
            
            # 2. Truncate and insert teacher_subjects (qualifications)
            cur.execute("TRUNCATE TABLE teacher_subjects;")
            relation_count = 0
            for kode_guru, mapel_list in TEACHER_SUBJECTS.items():
                id_guru = teacher_map.get(kode_guru)
                if not id_guru:
                    continue
                for nama_mapel in mapel_list:
                    id_mapel = subject_map.get(nama_mapel)
                    if id_mapel:
                        cur.execute("""
                            INSERT INTO teacher_subjects (id_guru, id_mapel)
                            VALUES (%s, %s)
                        """, (id_guru, id_mapel))
                        relation_count += 1
            print(f"  -> Seeded {relation_count} teacher-subject qualifications.")
            
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            
        print("\nAll databases seeded with subjects and teacher qualification mapping successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
