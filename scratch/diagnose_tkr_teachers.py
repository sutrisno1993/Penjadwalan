from backend.database import get_db_connection
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    # We want to check subjects containing 'Kendaraan' or 'Motor' or 'TKR'
    cur.execute("""
        SELECT id_mapel, nama_mapel, kategori_mapel 
        FROM subjects 
        WHERE nama_mapel LIKE '%Kendaraan%' OR nama_mapel LIKE '%Mesin%' OR nama_mapel LIKE '%Sasis%' OR nama_mapel LIKE '%Kelistrikan%'
    """)
    subjects = cur.fetchall()
    
    print("=== TKR PRODUCTIVE SUBJECTS GLOBAL DEMAND ===")
    
    for s in subjects:
        mid = s['id_mapel']
        
        # Get allocations
        cur.execute("""
            SELECT cs.id_class_subject, c.nama_kelas, c.shift_operasional, cs.durasi_jp
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            WHERE cs.id_mapel = %s
        """, (mid,))
        allocs = cur.fetchall()
        
        if not allocs:
            continue
            
        print(f"\nSubject: {s['nama_mapel']} (ID: {mid})")
        
        # Get qualified teachers
        cur.execute("""
            SELECT t.id_guru, t.nama_guru, t.max_jp, t.shift_pagi, t.shift_siang
            FROM teacher_subjects ts
            JOIN teachers t ON ts.id_guru = t.id_guru
            WHERE ts.id_mapel = %s
        """, (mid,))
        teachers = cur.fetchall()
        
        total_jp_pagi = sum(a['durasi_jp'] for a in allocs if a['shift_operasional'] == 'PAGI')
        total_jp_siang = sum(a['durasi_jp'] for a in allocs if a['shift_operasional'] == 'SIANG')
        
        print(f"  Total Allocations: {len(allocs)} classes | PAGI: {total_jp_pagi} JP, SIANG: {total_jp_siang} JP")
        print("  Qualified Teachers:")
        for t in teachers:
            print(f"    - {t['nama_guru']} (Max: {t['max_jp']} JP | Pagi: {t['shift_pagi']}, Siang: {t['shift_siang']})")
        print("  Allocated Classes:")
        for a in allocs:
            print(f"    - {a['nama_kelas']} ({a['shift_operasional']}): {a['durasi_jp']} JP")
            
    conn.close()

if __name__ == '__main__':
    main()
