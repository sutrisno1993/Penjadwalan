import pymysql

def main():
    print("================ EMPTYING ALL DATABASES ================")
    db_config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": ""
    }
    
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    try:
        dbs = ["jadwal_bekasi", "jadwal_jakarta", "lms_db"]
        
        for db in dbs:
            print(f"\nProcessing database: {db}...")
            cur.execute(f"USE {db}")
            
            # Get all tables
            cur.execute("SHOW TABLES")
            tables = [row[0] for row in cur.fetchall()]
            
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table in tables:
                if table == "migrations":
                    print(f"  -> Skipping table '{table}' to preserve migration history.")
                    continue
                cur.execute(f"TRUNCATE TABLE {table};")
                print(f"  -> Truncated table: {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            
        print("\nAll databases have been completely emptied (except migrations tables)!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR emptying databases: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
