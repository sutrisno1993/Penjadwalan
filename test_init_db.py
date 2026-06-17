import sys
from dotenv import load_dotenv
sys.path.insert(0, 'd:/Jadwal')
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection

print("1. Connecting to DB...")
conn = get_db_connection()
print("Connected!")

print("2. Opening cursor...")
cur = conn.cursor()
print("Cursor opened!")

print("3. Dropping table curriculum_allocations...")
cur.execute("DROP TABLE IF EXISTS curriculum_allocations CASCADE;")
print("Dropped!")

print("4. Creating table teachers...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id_guru             SERIAL  PRIMARY KEY,
        nama_guru           TEXT    NOT NULL,
        kode_guru           INTEGER UNIQUE NOT NULL,
        hari_tersedia       TEXT    NOT NULL,
        shift_pagi          BOOLEAN DEFAULT TRUE,
        shift_siang         BOOLEAN DEFAULT TRUE,
        hari_tersedia_pagi  TEXT,
        hari_tersedia_siang TEXT,
        min_jp              INTEGER DEFAULT 2,
        max_jp              INTEGER DEFAULT 60
    );
""")
print("Created teachers!")

print("5. Altering teachers table...")
cur.execute("""
    ALTER TABLE teachers ADD COLUMN IF NOT EXISTS min_jp INTEGER DEFAULT 2;
    ALTER TABLE teachers ADD COLUMN IF NOT EXISTS max_jp INTEGER DEFAULT 60;
    ALTER TABLE teachers DROP COLUMN IF EXISTS ideal_min_jp;
    ALTER TABLE teachers DROP COLUMN IF EXISTS ideal_max_jp;
    ALTER TABLE teachers DROP COLUMN IF EXISTS max_jp_mutlak;
""")
print("Altered teachers!")

print("6. Creating table classes...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id_kelas          SERIAL PRIMARY KEY,
        nama_kelas        TEXT   UNIQUE NOT NULL,
        shift_operasional TEXT   CHECK (shift_operasional IN ('PAGI','SIANG')),
        tingkat           TEXT,
        jurusan           TEXT
    );
""")
print("Created classes!")

print("7. Creating table subjects...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id_mapel       SERIAL PRIMARY KEY,
        nama_mapel     TEXT   NOT NULL,
        kategori_mapel TEXT,
        tingkat        TEXT,
        jurusan        TEXT
    );
""")
print("Created subjects!")

print("8. Altering subjects and classes tables...")
cur.execute("ALTER TABLE subjects DROP CONSTRAINT IF EXISTS subjects_kategori_mapel_check;")
cur.execute("""
    ALTER TABLE classes ADD COLUMN IF NOT EXISTS tingkat TEXT;
    ALTER TABLE classes ADD COLUMN IF NOT EXISTS jurusan TEXT;
    ALTER TABLE subjects ADD COLUMN IF NOT EXISTS tingkat TEXT;
    ALTER TABLE subjects ADD COLUMN IF NOT EXISTS jurusan TEXT;
""")
print("Altered subjects and classes!")

print("9. Creating teacher_subjects table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_subjects (
        id_teacher_subject SERIAL PRIMARY KEY,
        id_guru            INTEGER REFERENCES teachers(id_guru) ON DELETE CASCADE,
        id_mapel           INTEGER REFERENCES subjects(id_mapel) ON DELETE CASCADE,
        UNIQUE(id_guru, id_mapel)
    );
""")
print("Created teacher_subjects!")

print("10. Creating class_subjects table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS class_subjects (
        id_class_subject SERIAL  PRIMARY KEY,
        id_kelas         INTEGER REFERENCES classes(id_kelas)  ON DELETE CASCADE,
        id_mapel         INTEGER REFERENCES subjects(id_mapel) ON DELETE CASCADE,
        durasi_jp        INTEGER NOT NULL,
        id_guru_mutlak   INTEGER REFERENCES teachers(id_guru) ON DELETE SET NULL,
        UNIQUE(id_kelas, id_mapel)
    );
""")
print("Created class_subjects!")

print("11. Altering class_subjects...")
cur.execute("""
    ALTER TABLE class_subjects ADD COLUMN IF NOT EXISTS id_guru_mutlak INTEGER REFERENCES teachers(id_guru) ON DELETE SET NULL;
""")
print("Altered class_subjects!")

print("12. Creating timetable...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        id_timetable     SERIAL  PRIMARY KEY,
        id_class_subject INTEGER REFERENCES class_subjects(id_class_subject) ON DELETE CASCADE,
        hari             TEXT    NOT NULL,
        jam_ke           INTEGER NOT NULL,
        id_guru          INTEGER REFERENCES teachers(id_guru)  ON DELETE SET NULL,
        is_fallback      BOOLEAN DEFAULT FALSE,
        original_guru_id INTEGER REFERENCES teachers(id_guru)  ON DELETE SET NULL
    );
""")
print("Created timetable!")

print("13. Creating settings table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
""")
print("Created system_settings!")

print("14. Committing...")
conn.commit()
print("Committed successfully!")

cur.close()
conn.close()
print("Finished initialization successfully!")
