import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

conn = get_db_connection()
try:
    rows = db_fetchall(conn, """
        SELECT c.shift_operasional, SUM(cs.durasi_jp) as total_jp, COUNT(c.id_kelas) as n_kelas
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE s.nama_mapel = 'Bahasa Indonesia'
        GROUP BY c.shift_operasional
    """)
    print("=== BAHASA INDONESIA JP DEMAND BY SHIFT ===")
    for r in rows:
        print(f"Shift: {r['shift_operasional']} - Demand: {r['total_jp']} JP ({r['n_kelas']} kelas)")
        
    print("\n=== BAHASA INDONESIA GURU SHIFT LIMITS ===")
    teachers = db_fetchall(conn, """
        SELECT t.id_guru, t.nama_guru, t.shift_pagi, t.shift_siang, t.max_jp
        FROM teacher_subjects ts
        JOIN teachers t ON ts.id_guru = t.id_guru
        WHERE ts.id_mapel = (SELECT id_mapel FROM subjects WHERE nama_mapel = 'Bahasa Indonesia')
    """)
    for t in teachers:
        print(f"Guru: {t['nama_guru']}, Pagi: {t['shift_pagi']}, Siang: {t['shift_siang']}, Max JP: {t['max_jp']}")
        
finally:
    conn.close()
