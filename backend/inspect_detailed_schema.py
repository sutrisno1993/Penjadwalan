import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def main():
    conn = get_db_connection()
    try:
        print("--- Table Columns ---")
        for table in ["teachers", "classes", "subjects", "teacher_subjects", "class_subjects", "timetable"]:
            cols = db_fetchall(conn, f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'")
            print(f"\nTable: {table}")
            for col in cols:
                print(f"  - {col['column_name']} ({col['data_type']}) Nullable: {col['is_nullable']}")

        print("\n--- Constraints ---")
        for table in ["class_subjects", "timetable"]:
            constraints = db_fetchall(conn, f"""
                SELECT conname, pg_get_constraintdef(oid) as def 
                FROM pg_constraint 
                WHERE conrelid = '{table}'::regclass
            """)
            print(f"\nTable: {table}")
            for c in constraints:
                print(f"  - {c['conname']}: {c['def']}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
