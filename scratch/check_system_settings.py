import pymysql

conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="", database="jadwal_bekasi")
cur = conn.cursor(pymysql.cursors.DictCursor)
try:
    cur.execute("SELECT * FROM system_settings")
    rows = cur.fetchall()
    print("system_settings rows:", rows)
except Exception as e:
    print("Error:", e)
finally:
    cur.close()
    conn.close()
