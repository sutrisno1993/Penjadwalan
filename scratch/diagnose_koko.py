from backend.database import get_db_connection
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get teacher Koko's details
    cur.execute("SELECT id_guru, nama_guru, max_jp FROM teachers WHERE nama_guru LIKE '%KOKO%'")
    koko = cur.fetchone()
    if not koko:
        print("Koko not found")
        return
    
    print(f"Teacher: {koko['nama_guru']} (ID: {koko['id_guru']})")
    print(f"Max JP: {koko['max_jp']}")
    
    # Get Koko's qualified subjects
    cur.execute("""
        SELECT s.id_mapel, s.nama_mapel, s.kategori_mapel
        FROM teacher_subjects ts
        JOIN subjects s ON ts.id_mapel = s.id_mapel
        WHERE ts.id_guru = %s
    """, (koko['id_guru'],))
    subjects = cur.fetchall()
    print("\nQualified Subjects:")
    for s in subjects:
        print(f"  - ID {s['id_mapel']}: {s['nama_mapel']} (Kategori: {s['kategori_mapel']})")
        
    # Get all allocations of these subjects
    subject_ids = [s['id_mapel'] for s in subjects]
    cur.execute("""
        SELECT cs.id_class_subject, c.nama_kelas, c.shift_operasional, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE cs.id_mapel IN %s
    """, (tuple(subject_ids),))
    allocs = cur.fetchall()
    
    print("\nAllocations for these subjects:")
    total_jp = 0
    for a in allocs:
        mutlak = f" (MUTLAK locked to ID {a['id_guru_mutlak']})" if a['id_guru_mutlak'] else ""
        print(f"  - Kelas: {a['nama_kelas']} ({a['shift_operasional']}) | {a['nama_mapel']} | {a['durasi_jp']} JP{mutlak}")
        total_jp += a['durasi_jp']
    
    print(f"\nTotal JP demand for these subjects: {total_jp} JP")
    
    conn.close()

if __name__ == '__main__':
    main()
