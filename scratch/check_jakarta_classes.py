from backend.database import set_thread_branch, get_db_connection, db_fetchall

set_thread_branch('jakarta')
conn = get_db_connection()
classes = db_fetchall(conn, "SELECT nama_kelas, shift_operasional, tingkat, jurusan FROM classes ORDER BY id_kelas")
conn.close()

print("=== JAKARTA CLASSES (Total: %d) ===" % len(classes))
for c in classes:
    print("%s | Shift: %s | Tingkat: %s | Jurusan: %s" % (c['nama_kelas'], c['shift_operasional'], c['tingkat'], c['jurusan']))
