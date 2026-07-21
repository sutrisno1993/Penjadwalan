import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='jadwal_jakarta', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

cur.execute("SELECT id_guru, kode_guru, nama_guru, hari_tersedia, hari_tersedia_pagi, hari_tersedia_siang FROM teachers LIMIT 15;")
rows = cur.fetchall()
conn.close()

print("=== JADWAL_JAKARTA TEACHERS AVAILABILITY ===")
for r in rows:
    print(f"Guru {r['kode_guru']:2}: {r['nama_guru']:30} | Default: {r['hari_tersedia']} | Pagi: {r['hari_tersedia_pagi']} | Siang: {r['hari_tersedia_siang']}")
