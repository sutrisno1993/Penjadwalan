import pymysql

db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "jadwal_bekasi"
}

try:
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print("Tables in jadwal_bekasi:", [t[0] for t in tables])
except Exception as e:
    print("Error:", e)
finally:
    try:
        cur.close()
        conn.close()
    except:
        pass
