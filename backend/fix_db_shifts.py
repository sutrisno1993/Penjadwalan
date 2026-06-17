import os
from dotenv import load_dotenv
from backend.database import get_db_connection

load_dotenv()

def fix_shifts():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Update tingkat, jurusan, and shift_operasional if they are null
        # 1. Update shift_operasional
        cur.execute("""
            UPDATE classes 
            SET shift_operasional = CASE 
                WHEN nama_kelas LIKE 'XI %' OR nama_kelas LIKE 'XI%' THEN 'SIANG'
                ELSE 'PAGI'
            END
            WHERE shift_operasional IS NULL
        """)
        # 2. Update tingkat
        cur.execute("""
            UPDATE classes 
            SET tingkat = CASE 
                WHEN nama_kelas LIKE 'X %' THEN 'X'
                WHEN nama_kelas LIKE 'XI %' THEN 'XI'
                WHEN nama_kelas LIKE 'XII %' THEN 'XII'
                ELSE tingkat
            END
            WHERE tingkat IS NULL
        """)
        # 3. Update jurusan
        cur.execute("""
            UPDATE classes 
            SET jurusan = CASE 
                WHEN nama_kelas LIKE '% AK %' OR nama_kelas LIKE '% AK' THEN 'AK'
                WHEN nama_kelas LIKE '% OTKP %' OR nama_kelas LIKE '% OTKP' THEN 'OTKP'
                WHEN nama_kelas LIKE '% TKJ %' OR nama_kelas LIKE '% TKJ' THEN 'TKJ'
                WHEN nama_kelas LIKE '% TKR %' OR nama_kelas LIKE '% TKR' THEN 'TKR'
                WHEN nama_kelas LIKE '% TSM %' OR nama_kelas LIKE '% TSM' THEN 'TSM'
                ELSE jurusan
            END
            WHERE jurusan IS NULL
        """)
        conn.commit()
        print("Successfully updated missing shifts, tingkat, and jurusan in the classes table.")
    except Exception as e:
        conn.rollback()
        print("Error fixing database shifts:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_shifts()
