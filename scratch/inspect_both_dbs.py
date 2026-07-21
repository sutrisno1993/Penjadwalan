import pymysql

def check_db(dbname):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='', database=dbname, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM teachers")
        t_cnt = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM classes")
        c_cnt = cur.fetchone()['cnt']
        cur.execute("SELECT nama_guru FROM teachers LIMIT 5")
        gurus = [r['nama_guru'] for r in cur.fetchall()]
        cur.execute("SELECT nama_kelas FROM classes LIMIT 5")
        classes = [r['nama_kelas'] for r in cur.fetchall()]
        conn.close()
        print(f"=== DATABASE: {dbname} ===")
        print(f"Teachers count : {t_cnt}")
        print(f"Sample Teachers: {gurus}")
        print(f"Classes count  : {c_cnt}")
        print(f"Sample Classes : {classes}\n")
    except Exception as e:
        print(f"=== DATABASE: {dbname} ERROR: {e} ===\n")

check_db('jadwal_bekasi')
check_db('jadwal_jakarta')
