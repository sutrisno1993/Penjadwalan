import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch, db_fetchall

def main():
    active_branch.set("jakarta")
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT COUNT(*) as c FROM teachers")[0]['c']
        classes = db_fetchall(conn, "SELECT COUNT(*) as c FROM classes")[0]['c']
        subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM subjects")[0]['c']
        teacher_subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM teacher_subjects")[0]['c']
        class_subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM class_subjects")[0]['c']
        timetable = db_fetchall(conn, "SELECT COUNT(*) as c FROM timetable")[0]['c']
        
        print(f"JAKARTA SCHEMA COUNTS:")
        print(f"Teachers: {teachers}")
        print(f"Classes: {classes}")
        print(f"Subjects: {subjects}")
        print(f"Teacher-Subjects (qualifications): {teacher_subjects}")
        print(f"Class-Subjects (allocations): {class_subjects}")
        print(f"Timetable: {timetable}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
