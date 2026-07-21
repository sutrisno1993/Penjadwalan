import pymysql
import os
from dotenv import load_dotenv

load_dotenv('d:/Jadwal/.env')

def inspect():
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": ""
    }
    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    try:
        # Get all databases
        cur.execute("SHOW DATABASES")
        dbs = [row[0] for row in cur.fetchall() if row[0] in ['lms_db', 'jadwal_bekasi', 'jadwal_jakarta']]
        
        for db in dbs:
            print(f"\n================ DATABASE: {db} ================")
            cur.execute(f"USE {db}")
            cur.execute("SHOW TABLES")
            tables = [row[0] for row in cur.fetchall()]
            for table in tables:
                cur.execute(f"DESCRIBE {table}")
                cols = cur.fetchall()
                for col in cols:
                    col_name = col[0]
                    if 'guru' in col_name.lower():
                        print(f"Table: {table} | Column: {col_name} ({col[1]})")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    inspect()
