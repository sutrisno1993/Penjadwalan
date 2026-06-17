from backend.database import get_db_connection
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get class XI TKR 2 ID
    cur.execute("SELECT id_kelas, nama_kelas, shift_operasional FROM classes WHERE nama_kelas = 'XI TKR 2'")
    kelas = cur.fetchone()
    if not kelas:
        print("XI TKR 2 class not found")
        return
        
    print(f"Class: {kelas['nama_kelas']} (ID: {kelas['id_kelas']}, Shift: {kelas['shift_operasional']})")
    
    # Get allocations for this class
    cur.execute("""
        SELECT cs.id_class_subject, s.id_mapel, s.nama_mapel, s.kategori_mapel, cs.durasi_jp
        FROM class_subjects cs
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE cs.id_kelas = %s
    """, (kelas['id_kelas'],))
    allocs = cur.fetchall()
    
    print("\nAllocations for XI TKR 2:")
    for a in allocs:
        # Get qualified teachers for this subject in this shift
        cur.execute("""
            SELECT t.id_guru, t.nama_guru, t.max_jp
            FROM teacher_subjects ts
            JOIN teachers t ON ts.id_guru = t.id_guru
            WHERE ts.id_mapel = %s
              AND ((%s = 'PAGI' AND t.shift_pagi = TRUE) OR (%s = 'SIANG' AND t.shift_siang = TRUE))
        """, (a['id_mapel'], kelas['shift_operasional'], kelas['shift_operasional']))
        teachers = cur.fetchall()
        
        t_names = [f"{t['nama_guru']} (Max {t['max_jp']})" for t in teachers]
        print(f"  - Mapel: {a['nama_mapel']} | {a['durasi_jp']} JP")
        print(f"    Qualified Teachers: {', '.join(t_names) if t_names else 'NONE!'}")
        
    conn.close()

if __name__ == '__main__':
    main()
