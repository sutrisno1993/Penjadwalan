import re
import sys
from backend.database import get_db_connection

SQL_FILE = r"d:\\Jadwal\\jadwal_jakarta_import.sql"

def load_sql():
    try:
        with open(SQL_FILE, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read {SQL_FILE}: {e}")
        sys.exit(1)
    # Remove comments and split statements
    statements = []
    stmt = ""
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("--") or line.startswith("/*"):
            continue
        stmt += " " + line
        if line.endswith(";"):
            # Only keep INSERT statements (ignore CREATE, ALTER, etc.)
            if stmt.strip().upper().startswith("INSERT"):
                statements.append(stmt.strip())
            stmt = ""
    return statements

def exec_sql(statements):
    conn = get_db_connection()
    cur = conn.cursor()
    for sql in statements:
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            # Log and continue (e.g., duplicate key)
            print(f"Error executing: {sql[:60]}... -> {e}")
    cur.close()
    conn.close()
    print("Import completed.")

if __name__ == "__main__":
    stmts = load_sql()
    exec_sql(stmts)
