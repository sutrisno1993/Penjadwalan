import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()
conn = get_db_connection()
try:
    print("--- JADWAL LUTHFI ---")
    rows = db_fetchall(conn, """
        SELECT t.hari, t.jam_ke, c.nama_kelas, s.nama_mapel
        FROM timetable t
        JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE t.id_guru = 13
        ORDER BY t.hari, t.jam_ke
    """)
    
    if not rows:
        print("Luthfi tidak mendapatkan jam pelajaran sama sekali.")
    else:
        for row in rows:
            print(f"{row['hari']} JP {row['jam_ke']}: {row['nama_kelas']} - {row['nama_mapel']}")

    print("\n--- CEK APAKAH ADA SENIN ---")
    has_senin = any(r['hari'] == 'SENIN' for r in rows)
    if has_senin:
        print("ERROR: Luthfi masih mendapatkan hari SENIN!")
    else:
        print("OK: Luthfi TIDAK mendapatkan hari SENIN.")
finally:
    conn.close()
