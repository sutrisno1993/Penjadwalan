import pymysql

def check_allocations():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Check lms_db allocations
        cur.execute("USE lms_db")
        cur.execute("""
            SELECT c.nama_kelas, s.nama_mapel, cs.durasi_jp 
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            ORDER BY c.nama_kelas, s.nama_mapel
        """)
        lms_allocs = cur.fetchall()
        
        # Check jadwal_bekasi allocations
        cur.execute("USE jadwal_bekasi")
        cur.execute("""
            SELECT c.nama_kelas, s.nama_mapel, cs.durasi_jp 
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            ORDER BY c.nama_kelas, s.nama_mapel
        """)
        bekasi_allocs = cur.fetchall()
        
        print(f"LMS Allocations Count: {len(lms_allocs)}")
        print(f"Bekasi Allocations Count: {len(bekasi_allocs)}")
        
        # Compare
        lms_map = {(a['nama_kelas'], a['nama_mapel']): a['durasi_jp'] for a in lms_allocs}
        bekasi_map = {(a['nama_kelas'], a['nama_mapel']): a['durasi_jp'] for a in bekasi_allocs}
        
        diff = []
        for k, v in lms_map.items():
            if k not in bekasi_map:
                diff.append(f"Only in LMS: {k} -> {v}")
            elif bekasi_map[k] != v:
                diff.append(f"Diff in duration: {k} | LMS: {v} | Bekasi: {bekasi_map[k]}")
                
        for k, v in bekasi_map.items():
            if k not in lms_map:
                diff.append(f"Only in Bekasi: {k} -> {v}")
                
        print("\nDifferences:")
        for d in diff[:30]:
            print(d)
        if len(diff) > 30:
            print(f"... and {len(diff) - 30} more differences.")
            
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    check_allocations()
