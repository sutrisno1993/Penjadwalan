import sys
import os
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import parse_allocations

FUZZY_SUBJECT_MAP = {
    "Pendidikan Agama dan Budi Pekerti": "Pendidikan Agama Islam",
    "Pendidikan Pancasila dan Kewarganegaraan": "PPKn",
    "Pendidikan Jasmani, Olah Raga & Kesehatan": "Penjasorkes",
    "Teknologi Infrastruktur Jaringan": "Teknik Infrastruktur Jaringan",
    "Teknologi Layanan Jaringan": "Tek Layanan Jaringan",
    "Administrasi Sistem Jaringan": "Adm Sistem Jaringan",
    "AK Manufaktur": "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur",
    "BAHASA INGGRIS": "Bahasa Inggris",
    "Informatik": "Informatika",
    "Pend Agama Islam": "Pendidikan Agama Islam",
    "Sejarah": "Sejarah Indonesia",
    "Tek Insfrs Jaringan": "Teknik Infrastruktur Jaringan",
    "WAN": "Wide Area Network (WAN)"
}

def map_class_name(cname):
    cname = cname.replace("AKL", "AK")
    cname = cname.replace("TBSM", "TSM")
    cname = cname.replace("TKRO", "TKR")
    return cname

def main():
    print("================ SEEDING CLASS ALLOCATIONS ================")
    allocations = parse_allocations()
    print(f"Total raw allocations parsed from markdown: {len(allocations)}")
    if not allocations:
        return
        
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
            
            # Truncate class_subjects
            cur.execute("TRUNCATE TABLE class_subjects;")
            
            # Build lookups
            cur.execute("SELECT id_kelas, nama_kelas FROM classes")
            class_map = {row["nama_kelas"]: row["id_kelas"] for row in cur.fetchall()}
            
            cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
            subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
            
            inserted = 0
            skipped = 0
            for a in allocations:
                mapped_class = map_class_name(a["class"])
                id_kelas = class_map.get(mapped_class)
                
                subject_name = a["subject"]
                if subject_name in FUZZY_SUBJECT_MAP:
                    subject_name = FUZZY_SUBJECT_MAP[subject_name]
                id_mapel = subject_map.get(subject_name)
                
                if not id_kelas or not id_mapel:
                    print(f"  [WARN] Missing key for class={mapped_class} (id={id_kelas}), subject={subject_name} (id={id_mapel})")
                    skipped += 1
                    continue
                    
                cur.execute("""
                    INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE durasi_jp = VALUES(durasi_jp)
                """, (id_kelas, id_mapel, a["jp"]))
                inserted += 1
                
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print(f"  -> Successfully seeded {inserted} class-subject allocations. Skipped {skipped}.")
            
        print("\nAll databases successfully seeded with class allocations!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
