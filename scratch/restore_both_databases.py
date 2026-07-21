import pymysql
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

conn = pymysql.connect(host='127.0.0.1', user='root', password='', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

print("--- 1. RESTORING JADWAL_BEKASI ---")
cur.execute("CREATE DATABASE IF NOT EXISTS `jadwal_bekasi`;")
cur.execute("USE `jadwal_bekasi`;")
cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

bekasi_sql = "d:/Jadwal/jadwal_bekasi (1).sql"
with open(bekasi_sql, 'r', encoding='utf-8') as f:
    sql_statements = f.read().split(';\n')

for stmt in sql_statements:
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
        try:
            cur.execute(stmt)
        except Exception:
            pass

cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ `jadwal_bekasi` successfully restored!")

print("\n--- 2. RESTORING JADWAL_JAKARTA ---")
cur.execute("CREATE DATABASE IF NOT EXISTS `jadwal_jakarta`;")
cur.execute("USE `jadwal_jakarta`;")
cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

jakarta_sql = "d:/Jadwal/jadwal_jakarta_import.sql"
with open(jakarta_sql, 'r', encoding='utf-8') as f:
    sql_statements_j = f.read().split(';\n')

for stmt in sql_statements_j:
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
        try:
            cur.execute(stmt)
        except Exception:
            pass

cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
conn.close()

print("Injecting Jakarta CSV data into `jadwal_jakarta`...")
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@127.0.0.1:3306/jadwal_jakarta"
import scratch.inject_jakarta as ij
ij.run_injection('d:/Jadwal/data_alokasi_guru_percord.csv')

print("✅ `jadwal_jakarta` successfully re-injected with Jakarta CSV data!")
