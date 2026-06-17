import os
import json
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall, db_fetchone

load_dotenv()
conn = get_db_connection()
try:
    # 1. Cek Luthfi
    luthfi = db_fetchone(conn, "SELECT id_guru, nama_guru, hari_tersedia_pagi, hari_tersedia_siang, max_jp FROM teachers WHERE nama_guru LIKE %s", ('%LUTHFI%',))
    print('--- DATA LUTHFI ---')
    print(luthfi)
    
    # 2. Cek Guru Bahasa Indonesia lainnya
    others = db_fetchall(conn, """
        SELECT g.nama_guru, g.hari_tersedia_pagi, g.hari_tersedia_siang, g.max_jp
        FROM teacher_subjects ts
        JOIN teachers g ON ts.id_guru = g.id_guru
        WHERE ts.id_mapel = (SELECT id_mapel FROM subjects WHERE nama_mapel = 'Bahasa Indonesia')
        AND g.nama_guru NOT LIKE %s
    """, ('%LUTHFI%',))
    print('\n--- GURU BAHASA INDONESIA LAINNYA ---')
    for g in others:
        print(g)
        
    # 3. Cek total kebutuhan Bahasa Indonesia
    demand = db_fetchone(conn, "SELECT SUM(durasi_jp) as total FROM class_subjects WHERE id_mapel = (SELECT id_mapel FROM subjects WHERE nama_mapel = 'Bahasa Indonesia')")
    print(f'\nTotal Kebutuhan Bahasa Indonesia: {demand["total"]} JP')
finally:
    conn.close()
