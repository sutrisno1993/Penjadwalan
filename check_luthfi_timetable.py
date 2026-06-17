import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()
conn = get_db_connection()
try:
    # Cek jadwal Luthfi
    rows = db_fetchall(conn, """
        SELECT t.hari, t.jam_ke, c.nama_kelas, s.nama_mapel, t.is_fallback
        FROM timetable t
        JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
        WHERE t.id_guru = 13
        ORDER BY t.hari, t.jam_ke
    """)
    
    print('--- JADWAL LUTHFI DI DATABASE ---')
    for r in rows:
        print(r)
finally:
    conn.close()
