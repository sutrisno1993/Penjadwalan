from backend.database import set_thread_branch, get_db_connection, db_fetchall

set_thread_branch('jakarta')
conn_j = get_db_connection()
rows_j = db_fetchall(conn_j, """
    SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, g.kode_guru, g.nama_guru 
    FROM class_subjects cs 
    JOIN classes c ON cs.id_kelas=c.id_kelas 
    JOIN subjects s ON cs.id_mapel=s.id_mapel 
    LEFT JOIN teachers g ON cs.id_guru_mutlak=g.id_guru 
    LIMIT 10
""")
conn_j.close()

print("=== JAKARTA SAMPLE ALLOCATIONS RESTORED ===")
for r in rows_j:
    guru_str = "[Kode %s] %s" % (r['kode_guru'], r['nama_guru']) if r['kode_guru'] else "BELUM ADA"
    print("%s | %s | %d JP | Guru: %s" % (r['nama_kelas'], r['nama_mapel'], r['durasi_jp'], guru_str))
