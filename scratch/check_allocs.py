from backend.database import get_db_connection
from dotenv import load_dotenv
import sys

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.id_kelas, c.nama_kelas, c.shift_operasional, 
               COALESCE(SUM(cs.durasi_jp), 0) AS total_jp
        FROM classes c
        LEFT JOIN class_subjects cs ON c.id_kelas = cs.id_kelas
        GROUP BY c.id_kelas, c.nama_kelas, c.shift_operasional
        ORDER BY c.nama_kelas
    ''')
    rows = cur.fetchall()
    print("=== DATA KELAS DAN TOTAL ALOKASI JP ===")
    for r in rows:
        print(f"ID: {r['id_kelas']} | Kelas: {r['nama_kelas']} | Shift: {r['shift_operasional']} | Total JP: {r['total_jp']}")
    
    # Check if there are allocations without a qualified teacher
    cur.execute('''
        SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        LEFT JOIN teacher_subjects ts ON cs.id_mapel = ts.id_mapel
        WHERE ts.id_guru IS NULL
    ''')
    no_teacher_rows = cur.fetchall()
    print("\n=== ALOKASI MATA PELAJARAN YANG TIDAK PUNYA GURU SAMA SEKALI ===")
    if no_teacher_rows:
        for nr in no_teacher_rows:
            print(f"Kelas: {nr['nama_kelas']} | Mapel: {nr['nama_mapel']} | Durasi: {nr['durasi_jp']} JP")
    else:
        print("Semua alokasi memiliki minimal satu guru berkualifikasi.")
        
    conn.close()

if __name__ == '__main__':
    main()
