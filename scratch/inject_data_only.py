import os
import sys
import re

sys.path.insert(0, '.')
import backend.database as db

sql_file = r'd:\Jadwal_BKS\jadwal_bekasi (1).sql'

print("=== STARTING DATA INJECTION ===")
print(f"Reading SQL file: {sql_file}")

with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Extract only INSERT INTO statements
# Split statements by semicolon while looking for INSERT INTO
statements = []
current_stmt = []
in_insert = False

for line in content.splitlines():
    stripped = line.strip()
    if stripped.upper().startswith("INSERT INTO"):
        in_insert = True
        current_stmt.append(line)
    elif in_insert:
        current_stmt.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current_stmt))
            current_stmt = []
            in_insert = False

print(f"Found {len(statements)} INSERT statement blocks.")

# Identify target tables to clear data before inserting
target_tables = set()
for stmt in statements:
    match = re.search(r'INSERT INTO `?(\w+)`?', stmt, re.IGNORECASE)
    if match:
        target_tables.add(match.group(1))

print("Target tables to update data:", list(target_tables))

conn = db.get_db_connection()
cur = conn.cursor()

try:
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # Empty existing data in target tables only (without dropping tables)
    for table in target_tables:
        print(f"Clearing existing rows in table '{table}'...")
        cur.execute(f"DELETE FROM `{table}`;")

    inserted_counts = {t: 0 for t in target_tables}

    # Execute INSERT statements
    for stmt in statements:
        match = re.search(r'INSERT INTO `?(\w+)`?', stmt, re.IGNORECASE)
        table = match.group(1) if match else "unknown"
        cur.execute(stmt)
        if table in inserted_counts:
            inserted_counts[table] += cur.rowcount

    conn.commit()
    print("\n=== DATA INJECTION COMPLETED SUCCESSFULLY ===")
    print("Rows inserted per table:")
    for table, count in inserted_counts.items():
        print(f"  - Table '{table}': {count} rows inserted")

except Exception as e:
    conn.rollback()
    print(f"\n[ERROR] Failed to inject data: {e}")
    raise e
finally:
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cur.close()
        conn.close()
    except Exception:
        pass
