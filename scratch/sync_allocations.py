import pymysql

def sync_allocations():
    print("Syncing class allocations from lms_db to jadwal_bekasi...")
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 1. Fetch allocations from lms_db
        cur.execute("USE lms_db")
        cur.execute("""
            SELECT c.nama_kelas, s.nama_mapel, cs.durasi_jp, t.kode_guru AS kode_guru_mutlak
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            LEFT JOIN teachers t ON cs.id_guru_mutlak = t.id_guru
        """)
        lms_allocs = cur.fetchall()
        print(f"  -> Fetched {len(lms_allocs)} allocations from lms_db.")
        
        # 2. Switch to jadwal_bekasi
        cur.execute("USE jadwal_bekasi")
        
        # Build lookups for classes, subjects, and teachers in jadwal_bekasi
        cur.execute("SELECT id_kelas, nama_kelas FROM classes")
        class_map = {row["nama_kelas"]: row["id_kelas"] for row in cur.fetchall()}
        
        cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
        subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
        
        cur.execute("SELECT id_guru, kode_guru FROM teachers")
        teacher_map = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}
        
        # 3. Truncate class_subjects in jadwal_bekasi
        # We need to disable foreign key checks temporarily to safely delete
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE class_subjects")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("  -> Cleared existing allocations in jadwal_bekasi.")
        
        # 4. Insert restored allocations
        inserted = 0
        skipped = 0
        for alloc in lms_allocs:
            id_kelas = class_map.get(alloc["nama_kelas"])
            id_mapel = subject_map.get(alloc["nama_mapel"])
            
            if not id_kelas or not id_mapel:
                print(f"  [WARN] Class '{alloc['nama_kelas']}' or Subject '{alloc['nama_mapel']}' not found in jadwal_bekasi. Skipping.")
                skipped += 1
                continue
                
            id_guru_mutlak = None
            if alloc["kode_guru_mutlak"] is not None:
                id_guru_mutlak = teacher_map.get(alloc["kode_guru_mutlak"])
                if not id_guru_mutlak:
                    print(f"  [WARN] Teacher with code {alloc['kode_guru_mutlak']} not found in jadwal_bekasi.")
            
            cur.execute("""
                INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak)
                VALUES (%s, %s, %s, %s)
            """, (id_kelas, id_mapel, alloc["durasi_jp"], id_guru_mutlak))
            inserted += 1
            
        conn.commit()
        print(f"Sync complete! Inserted {inserted} allocations, skipped {skipped}.")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR syncing allocations: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    sync_allocations()
