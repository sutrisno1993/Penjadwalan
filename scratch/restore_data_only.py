import os
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection, active_branch, clear_master_data

def main():
    # Set branch to bekasi explicitly
    active_branch.set("bekasi")
    
    print("Emptying existing data in bekasi database...")
    clear_master_data()

    sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jadwal_bekasi (1).sql'))
    if not os.path.exists(sql_file_path):
        print(f"File {sql_file_path} not found!")
        return

    print("Reading SQL dump file...")
    with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract all INSERT INTO statements
    pattern = re.compile(r'INSERT INTO `?(\w+)`?[^;]+;', re.IGNORECASE)
    raw_matches = re.finditer(r'INSERT INTO `?(\w+)`?[^;]+;', content, re.IGNORECASE)

    conn = get_db_connection(branch="bekasi")
    cur = conn.cursor()

    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        count = 0
        for match in raw_matches:
            stmt = match.group(0)
            table_name = match.group(1)
            
            # Replace INSERT INTO with REPLACE INTO to overwrite duplicates
            stmt_replace = re.sub(r'^INSERT INTO', 'REPLACE INTO', stmt, flags=re.IGNORECASE)
            
            try:
                cur.execute(stmt_replace)
                count += 1
            except Exception as e:
                print(f"Error inserting into {table_name}: {e}")

        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print(f"Successfully executed {count} INSERT statements into 'jadwal_bekasi' database.")
    except Exception as e:
        conn.rollback()
        print(f"Failed to restore data: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
