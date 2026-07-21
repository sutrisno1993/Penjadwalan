import pymysql

def main():
    print("================ ROLLBACK: KEEPING ONLY TEACHERS ================")
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
        tables_to_truncate = ["timetable", "class_subjects", "teacher_subjects", "classes", "subjects"]
        
        for db in dbs:
            print(f"Truncating master & transaction tables in: {db} (keeping teachers)...")
            cur.execute(f"USE {db}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table in tables_to_truncate:
                cur.execute(f"TRUNCATE TABLE {table};")
                print(f"  -> Truncated: {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            
        print("\nRollback complete! All tables are empty except for the 'teachers' table.")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR running rollback: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
