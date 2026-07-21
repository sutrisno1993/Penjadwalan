from backend.database import set_thread_branch, get_db_connection, db_fetchall

set_thread_branch('jakarta')
conn = get_db_connection()
tj = db_fetchall(conn, "SELECT kode_guru, nama_guru FROM teachers ORDER BY kode_guru")
conn.close()

set_thread_branch('bekasi')
conn = get_db_connection()
tb = db_fetchall(conn, "SELECT kode_guru, nama_guru FROM teachers ORDER BY kode_guru")
conn.close()

print("=== JAKARTA TEACHERS (Total: %d) ===" % len(tj))
for t in tj[:10]:
    print("  Kode %s: %s" % (t['kode_guru'], t['nama_guru']))

print("\n=== BEKASI TEACHERS (Total: %d) ===" % len(tb))
for t in tb[:10]:
    print("  Kode %s: %s" % (t['kode_guru'], t['nama_guru']))
