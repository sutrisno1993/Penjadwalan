import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def inspect():
    conn = get_db_connection()
    try:
        teachers = db_fetchall(conn, "SELECT COUNT(*) as c FROM teachers")[0]['c']
        classes = db_fetchall(conn, "SELECT COUNT(*) as c FROM classes")[0]['c']
        subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM subjects")[0]['c']
        teacher_subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM teacher_subjects")[0]['c']
        class_subjects = db_fetchall(conn, "SELECT COUNT(*) as c FROM class_subjects")[0]['c']
        timetable = db_fetchall(conn, "SELECT COUNT(*) as c FROM timetable")[0]['c']
        
        print(f"Teachers: {teachers}")
        print(f"Classes: {classes}")
        print(f"Subjects: {subjects}")
        print(f"Teacher-Subjects (qualifications): {teacher_subjects}")
        print(f"Class-Subjects (allocations): {class_subjects}")
        print(f"Timetable: {timetable}")
        
        if classes > 0:
            print("\nClasses Sample:")
            for c in db_fetchall(conn, "SELECT id_kelas, nama_kelas, shift_operasional FROM classes LIMIT 5"):
                print(c)
        if teachers > 0:
            print("\nTeachers Sample:")
            for t in db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru FROM teachers LIMIT 5"):
                print(t)
        if subjects > 0:
            print("\nSubjects Sample:")
            for s in db_fetchall(conn, "SELECT id_mapel, nama_mapel, kategori_mapel FROM subjects LIMIT 5"):
                print(s)
                
    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
