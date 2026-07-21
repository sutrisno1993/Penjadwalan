import pymysql

def print_teachers(db):
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(f"USE {db}")
        cur.execute("SELECT id_guru, nama_guru, kode_guru FROM teachers ORDER BY id_guru LIMIT 20")
        print(f"\n{db} Teachers:")
        for row in cur.fetchall():
            print(f"ID: {row['id_guru']} | Name: {row['nama_guru']} | Code: {row['kode_guru']}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print_teachers("jadwal_bekasi")
    print_teachers("jadwal_jakarta")
