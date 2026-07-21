import re
import backend.database as db

sql_file = r'd:\Jadwal_BKS\jadwal_bekasi (1).sql'

with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

creates = re.findall(r'CREATE TABLE IF NOT EXISTS `?(\w+)`?|CREATE TABLE `?(\w+)`?', content, re.IGNORECASE)
create_tables = [c[0] or c[1] for c in creates]

inserts = re.findall(r'INSERT INTO `?(\w+)`?', content, re.IGNORECASE)

print("Tables in SQL Dump (CREATE TABLE):", set(create_tables))
print("Tables with Data (INSERT INTO):", set(inserts))

# Check existing tables in jadwal_bekasi database
try:
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    db_tables = [list(row.values())[0] for row in cur.fetchall()]
    print("\nExisting Tables in 'jadwal_bekasi' DB:", db_tables)
    cur.close()
    conn.close()
except Exception as e:
    print("Error connecting to DB:", e)
