import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

conn = get_db_connection()
try:
    # 1. Total Olahraga allocations
    rows = db_fetchall(conn, """
        SELECT cs.id_class_subject, c.nama_kelas, c.shift_operasional, s.nama_mapel, cs.durasi_jp
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE s.nama_mapel = 'Penjasorkes'
    """)
    print("=== ALOKASI OLAHRAGA (PENJASORKES) ===")
    pagi = 0
    siang = 0
    for r in rows:
        print(f"Kelas: {r['nama_kelas']}, Shift: {r['shift_operasional']}, Durasi: {r['durasi_jp']}")
        if r['shift_operasional'] == 'PAGI':
            pagi += 1
        else:
            siang += 1
            
    print(f"\nTotal Olahraga Pagi: {pagi} kelas ({pagi * 2} JP)")
    print(f"Total Olahraga Siang: {siang} kelas ({siang * 2} JP)")
    
    # 2. Qualified teachers for Penjasorkes
    teachers = db_fetchall(conn, """
        SELECT t.id_guru, t.nama_guru, t.kode_guru, t.shift_pagi, t.shift_siang, t.hari_tersedia_pagi, t.hari_tersedia_siang
        FROM teacher_subjects ts
        JOIN teachers t ON ts.id_guru = t.id_guru
        WHERE ts.id_mapel = (SELECT id_mapel FROM subjects WHERE nama_mapel = 'Penjasorkes')
    """)
    print("\n=== GURU OLAHRAGA KUALIFIKASI ===")
    for t in teachers:
        print(f"ID: {t['id_guru']}, Kode: {t['kode_guru']}, Nama: {t['nama_guru']}")
        print(f"  Pagi: {t['shift_pagi']} - {t['hari_tersedia_pagi']}")
        print(f"  Siang: {t['shift_siang']} - {t['hari_tersedia_siang']}")
finally:
    conn.close()
