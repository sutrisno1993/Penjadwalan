"""
database.py — Koneksi dan inisialisasi schema ke Supabase (PostgreSQL)
"""
import os
import logging
from contextvars import ContextVar
import psycopg2
import psycopg2.extras
import psycopg2.pool

logger = logging.getLogger(__name__)

# ContextVar untuk menyimpan cabang/skema aktif (bekasi atau jakarta)
active_branch: ContextVar[str] = ContextVar("active_branch", default="bekasi")


# ─────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────

def _get_db_url() -> str:
    """
    Membaca URL koneksi PostgreSQL dari environment variable.
    Priority:
      1. DATABASE_URL  (full postgres:// atau postgresql:// URL)
      2. DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        
        # Robust DNS fallback: resolve host to IP dynamically to prevent
        # "could not translate host name" OperationalError on flaky local DNS.
        try:
            import urllib.parse as urlparse
            import socket
            socket.setdefaulttimeout(5.0)
            parsed = urlparse.urlparse(url)
            if parsed.hostname:
                try:
                    ip = socket.gethostbyname(parsed.hostname)
                except Exception:
                    # Fallback to known Australian Supabase Pooler IPs if DNS fails completely
                    if "supabase" in parsed.hostname:
                        ip = "13.239.87.90"
                    else:
                        raise
                netloc = parsed.netloc.replace(parsed.hostname, ip)
                url = urlparse.urlunparse(parsed._replace(netloc=netloc))
        except Exception as e:
            logger.warning(f"Bypassing DNS lookup optimization: {e}")
        return url

    host     = os.environ.get("DB_HOST", "").strip()
    port     = os.environ.get("DB_PORT", "5432").strip()
    dbname   = os.environ.get("DB_NAME", "postgres").strip()
    user     = os.environ.get("DB_USER", "postgres").strip()
    password = os.environ.get("DB_PASSWORD", "").strip()

    if host:
        try:
            import socket
            resolved_host = socket.gethostbyname(host)
            host = resolved_host
        except Exception:
            if "supabase" in host:
                host = "13.239.87.90"

    if not host:
        raise RuntimeError(
            "DATABASE_URL belum dikonfigurasi!\n"
            "Isi file .env dengan DATABASE_URL dari Supabase Dashboard."
        )
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


class ConnectionWrapper:
    def __init__(self, conn, pool=None):
        self._conn = conn
        self._pool = pool

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        if self._conn is not None:
            if self._pool is not None:
                try:
                    # Rollback transaction to clean connection state
                    self._conn.rollback()
                except Exception:
                    pass
                self._pool.putconn(self._conn)
            else:
                self._conn.close()
            self._conn = None
            self._pool = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.__exit__(exc_type, exc_val, exc_tb)

_connection_pool = None

def get_db_connection():
    """Mengembalikan koneksi psycopg2 dengan RealDictCursor (row → dict) dari connection pool."""
    global _connection_pool
    url = _get_db_url()
    
    if _connection_pool is None:
        try:
            logger.info("Initializing ThreadedConnectionPool (min=2, max=20)...")
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                dsn=url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}. Falling back to direct connections.")
            
    wrapped_conn = None
    if _connection_pool is not None:
        try:
            conn = _connection_pool.getconn()
            conn.autocommit = False
            wrapped_conn = ConnectionWrapper(conn, _connection_pool)
        except Exception as e:
            logger.warning(f"Failed to get pooled connection: {e}. Falling back to direct connection.")
            
    if wrapped_conn is None:
        conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = False
        wrapped_conn = ConnectionWrapper(conn, None)

    # Set search_path to the active branch schema
    try:
        branch = active_branch.get().lower()
        if branch not in ["bekasi", "jakarta"]:
            branch = "bekasi"
        
        cur = wrapped_conn.cursor()
        cur.execute(f"SET search_path TO {branch};")
        cur.close()
    except Exception as e:
        logger.warning(f"Failed to set search_path to {active_branch.get()}: {e}")

    return wrapped_conn


# ─────────────────────────────────────────────
# Schema — DDL (idempotent)
# ─────────────────────────────────────────────

def init_db():
    """Membuat semua tabel jika belum ada di skema bekasi dan jakarta."""
    # Pertama, buat skema bekasi dan jakarta di database utama jika belum ada
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("CREATE SCHEMA IF NOT EXISTS bekasi;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS jakarta;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Gagal membuat schema bekasi/jakarta: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

    # Kedua, inisialisasi tabel untuk masing-masing skema
    for branch in ["bekasi", "jakarta"]:
        token = active_branch.set(branch)
        conn = get_db_connection()
        cur  = conn.cursor()
        try:
            cur.execute("DROP TABLE IF EXISTS curriculum_allocations CASCADE;")

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
                    max_jp              INTEGER DEFAULT 60,
                    allowed_jp_pagi     TEXT,
                    allowed_jp_siang    TEXT
                );
            """)

            cur.execute("""
                ALTER TABLE teachers ADD COLUMN IF NOT EXISTS min_jp INTEGER DEFAULT 2;
                ALTER TABLE teachers ADD COLUMN IF NOT EXISTS max_jp INTEGER DEFAULT 60;
                ALTER TABLE teachers ADD COLUMN IF NOT EXISTS allowed_jp_pagi TEXT;
                ALTER TABLE teachers ADD COLUMN IF NOT EXISTS allowed_jp_siang TEXT;
                ALTER TABLE teachers DROP COLUMN IF EXISTS ideal_min_jp;
                ALTER TABLE teachers DROP COLUMN IF EXISTS ideal_max_jp;
                ALTER TABLE teachers DROP COLUMN IF EXISTS max_jp_mutlak;
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id_kelas          SERIAL PRIMARY KEY,
                    nama_kelas        TEXT   UNIQUE NOT NULL,
                    shift_operasional TEXT   CHECK (shift_operasional IN ('PAGI','SIANG')),
                    tingkat           TEXT,
                    jurusan           TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id_mapel       SERIAL PRIMARY KEY,
                    nama_mapel     TEXT   NOT NULL,
                    kategori_mapel TEXT,
                    tingkat        TEXT,
                    jurusan        TEXT
                );
            """)

            cur.execute("ALTER TABLE subjects DROP CONSTRAINT IF EXISTS subjects_kategori_mapel_check;")

            cur.execute("""
                ALTER TABLE classes ADD COLUMN IF NOT EXISTS tingkat TEXT;
                ALTER TABLE classes ADD COLUMN IF NOT EXISTS jurusan TEXT;
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS tingkat TEXT;
                ALTER TABLE subjects ADD COLUMN IF NOT EXISTS jurusan TEXT;
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS teacher_subjects (
                    id_teacher_subject SERIAL PRIMARY KEY,
                    id_guru            INTEGER REFERENCES teachers(id_guru) ON DELETE CASCADE,
                    id_mapel           INTEGER REFERENCES subjects(id_mapel) ON DELETE CASCADE,
                    UNIQUE(id_guru, id_mapel)
                );
            """)

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

            cur.execute("""
                ALTER TABLE class_subjects ADD COLUMN IF NOT EXISTS id_guru_mutlak INTEGER REFERENCES teachers(id_guru) ON DELETE SET NULL;
            """)

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

            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

            conn.commit()
            logger.info(f"Schema Supabase/PostgreSQL untuk cabang '{branch}' berhasil diinisialisasi.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Gagal menginisialisasi skema cabang '{branch}': {e}")
            raise e
        finally:
            cur.close()
            conn.close()
            active_branch.reset(token)

    # Setelah skema diinisialisasi, migrasikan data dari public ke bekasi jika diperlukan
    migrate_public_to_bekasi()


def migrate_public_to_bekasi():
    """Menyalin data lama dari skema public ke skema bekasi jika skema bekasi masih kosong."""
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # Cek apakah tabel public.teachers ada di database
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'teachers'
            );
        """)
        public_exists = cur.fetchone()["exists"]
        if not public_exists:
            return
            
        cur.execute("SELECT COUNT(*) as count FROM public.teachers;")
        public_count = cur.fetchone()["count"]
        if public_count == 0:
            return
            
        # Cek apakah bekasi.teachers kosong
        cur.execute("SELECT COUNT(*) as count FROM bekasi.teachers;")
        bekasi_count = cur.fetchone()["count"]
        if bekasi_count > 0:
            return
            
        logger.info("Mendeteksi data lama di skema 'public'. Menyalin data ke skema 'bekasi'...")
        
        # Copy data secara eksplisit per kolom untuk menghindari error perbedaan urutan kolom
        cur.execute("""
            INSERT INTO bekasi.teachers (
                id_guru, nama_guru, kode_guru, hari_tersedia, shift_pagi, shift_siang, 
                hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp, allowed_jp_pagi, allowed_jp_siang
            ) 
            SELECT 
                id_guru, nama_guru, kode_guru, hari_tersedia, shift_pagi, shift_siang, 
                hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp, allowed_jp_pagi, allowed_jp_siang 
            FROM public.teachers 
            ON CONFLICT (id_guru) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.classes (id_kelas, nama_kelas, shift_operasional, tingkat, jurusan) 
            SELECT id_kelas, nama_kelas, shift_operasional, tingkat, jurusan 
            FROM public.classes 
            ON CONFLICT (id_kelas) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.subjects (id_mapel, nama_mapel, kategori_mapel, tingkat, jurusan) 
            SELECT id_mapel, nama_mapel, kategori_mapel, tingkat, jurusan 
            FROM public.subjects 
            ON CONFLICT (id_mapel) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.teacher_subjects (id_teacher_subject, id_guru, id_mapel) 
            SELECT id_teacher_subject, id_guru, id_mapel 
            FROM public.teacher_subjects 
            ON CONFLICT (id_teacher_subject) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.class_subjects (id_class_subject, id_kelas, id_mapel, durasi_jp, id_guru_mutlak) 
            SELECT id_class_subject, id_kelas, id_mapel, durasi_jp, id_guru_mutlak 
            FROM public.class_subjects 
            ON CONFLICT (id_class_subject) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.timetable (id_timetable, id_class_subject, hari, jam_ke, id_guru, is_fallback, original_guru_id) 
            SELECT id_timetable, id_class_subject, hari, jam_ke, id_guru, is_fallback, original_guru_id 
            FROM public.timetable 
            ON CONFLICT (id_timetable) DO NOTHING;
        """)
        
        cur.execute("""
            INSERT INTO bekasi.system_settings (key, value) 
            SELECT key, value 
            FROM public.system_settings 
            ON CONFLICT (key) DO NOTHING;
        """)
        
        # Reset sequences
        cur.execute("SELECT setval('bekasi.teachers_id_guru_seq', COALESCE((SELECT MAX(id_guru) FROM bekasi.teachers), 1));")
        cur.execute("SELECT setval('bekasi.classes_id_kelas_seq', COALESCE((SELECT MAX(id_kelas) FROM bekasi.classes), 1));")
        cur.execute("SELECT setval('bekasi.subjects_id_mapel_seq', COALESCE((SELECT MAX(id_mapel) FROM bekasi.subjects), 1));")
        cur.execute("SELECT setval('bekasi.teacher_subjects_id_teacher_subject_seq', COALESCE((SELECT MAX(id_teacher_subject) FROM bekasi.teacher_subjects), 1));")
        cur.execute("SELECT setval('bekasi.class_subjects_id_class_subject_seq', COALESCE((SELECT MAX(id_class_subject) FROM bekasi.class_subjects), 1));")
        cur.execute("SELECT setval('bekasi.timetable_id_timetable_seq', COALESCE((SELECT MAX(id_timetable) FROM bekasi.timetable), 1));")
        
        conn.commit()
        logger.info("Migrasi data dari 'public' ke skema 'bekasi' sukses!")
    except Exception as e:
        conn.rollback()
        logger.error(f"Gagal menyalin data dari public ke bekasi: {e}")
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
# Settings helpers
# ─────────────────────────────────────────────

def save_setting(key: str, value: str):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO system_settings (key,value) VALUES (%s,%s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (key, value)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_setting(key: str, default=None):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT value FROM system_settings WHERE key = %s", (key,))
        row = cur.fetchone()
        return row["value"] if row else default
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
# Bulk-clear (dipakai oleh API /api/clear)
# ─────────────────────────────────────────────

def clear_master_data():
    """Hapus semua data master + jadwal, reset auto-increment sequences."""
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "TRUNCATE TABLE timetable, class_subjects, teacher_subjects, "
            "teachers, classes, subjects RESTART IDENTITY CASCADE;"
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
# Convenience query helpers (dipakai oleh modul lain)
# ─────────────────────────────────────────────

def db_fetchall(conn, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    return rows


def db_fetchone(conn, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None


def db_execute(conn, sql: str, params=(), commit=True):
    cur = conn.cursor()
    cur.execute(sql, params)
    if commit:
        conn.commit()
    cur.close()


# ─────────────────────────────────────────────
# CLI entry-point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    init_db()
    print("Database Supabase berhasil diinisialisasi.")
