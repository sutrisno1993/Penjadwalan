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
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM settings")
    rows = cur.fetchall()
    print("Current settings in jadwal_bekasi:", rows)
    
    # Update any branch-related setting to 'bekasi' / 'Bekasi' if exists
    for r in rows:
        key = r.get('key_name') or r.get('k') or r.get('setting_key') or r.get('key')
        val = r.get('value_text') or r.get('v') or r.get('setting_value') or r.get('value')
        print(f"Setting key: {key}, val: {val}")
        if key and 'cabang' in str(key).lower():
            cur.execute("UPDATE settings SET value_text = 'bekasi' WHERE key_name = %s", (key,))
            conn.commit()
            print(f"Updated setting {key} to bekasi")
except Exception as e:
    print("Error inspecting settings table:", e)
finally:
    try:
        cur.close()
        conn.close()
    except:
        pass
