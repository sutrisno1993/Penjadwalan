"""
database.py — Koneksi dan inisialisasi schema ke MySQL
"""
import os
import logging
from contextvars import ContextVar
import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB

logger = logging.getLogger(__name__)

# ContextVar untuk menyimpan cabang/skema aktif (bekasi atau jakarta)
active_branch: ContextVar[str] = ContextVar("active_branch", default="bekasi")


# ─────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────

def _get_db_config():
    """
    Membaca konfigurasi MySQL.
    """
    host     = os.environ.get("DB_HOST", "127.0.0.1").strip()
    port     = int(os.environ.get("DB_PORT", "3306").strip())
    user     = os.environ.get("DB_USER", "root").strip()
    password = os.environ.get("DB_PASSWORD", "").strip()

    url = os.environ.get("DATABASE_URL", "").strip()
    if url and url.startswith("mysql"):
        # Very simple URL parsing for mysql+pymysql://user:pass@host:port/db
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(url.replace("mysql+pymysql://", "mysql://"))
        host = parsed.hostname or host
        port = parsed.port or port
        user = parsed.username or user
        password = parsed.password or password

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password
    }


class ConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        if self._conn is not None:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

_connection_pool = None

def get_db_connection(auto_create_db=False):
    """Mengembalikan koneksi MySQL dengan DictCursor (row → dict) dari connection pool."""
    global _connection_pool
    config = _get_db_config()
    
    branch = active_branch.get().lower()
    if branch not in ["bekasi", "jakarta"]:
        branch = "bekasi"
    
    # We map the branch to the database name
    db_name = f"jadwal_{branch}"

    if _connection_pool is None:
        try:
            logger.info("Initializing MySQL PooledDB...")
            _connection_pool = PooledDB(
                creator=pymysql,
                maxconnections=20,
                mincached=2,
                maxcached=5,
                maxshared=3,
                blocking=True,
                maxusage=None,
                setsession=[],
                ping=1,
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            
    wrapped_conn = None
    if _connection_pool is not None:
        try:
            conn = _connection_pool.connection()
            wrapped_conn = ConnectionWrapper(conn)
        except Exception as e:
            logger.warning(f"Failed to get pooled connection: {e}")
            
    if wrapped_conn is None:
        conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        wrapped_conn = ConnectionWrapper(conn)

    # Use the appropriate database for the branch
    try:
        cur = wrapped_conn.cursor()
        if auto_create_db:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        cur.execute(f"USE `{db_name}`;")
        cur.close()
    except Exception as e:
        logger.warning(f"Failed to USE database {db_name}: {e}")

    return wrapped_conn


# ─────────────────────────────────────────────
# Schema — DDL (idempotent)
# ─────────────────────────────────────────────

def init_db():
    """Membuat semua tabel jika belum ada di database bekasi dan jakarta."""
    # Pastikan database ada untuk masing-masing cabang
    for branch in ["bekasi", "jakarta"]:
        token = active_branch.set(branch)
        conn = get_db_connection(auto_create_db=True)
        cur  = conn.cursor()
        try:
            cur.execute("SET FOREIGN_KEY_CHECKS=0;")
            cur.execute("DROP TABLE IF EXISTS curriculum_allocations;")
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id_guru             INT AUTO_INCREMENT PRIMARY KEY,
                    nama_guru           VARCHAR(255) NOT NULL,
                    kode_guru           INT UNIQUE NOT NULL,
                    hari_tersedia       TEXT NOT NULL,
                    shift_pagi          TINYINT(1) DEFAULT 1,
                    shift_siang         TINYINT(1) DEFAULT 1,
                    hari_tersedia_pagi  TEXT,
                    hari_tersedia_siang TEXT,
                    min_jp              INT DEFAULT 2,
                    max_jp              INT DEFAULT 60,
                    allowed_jp_pagi     TEXT,
                    allowed_jp_siang    TEXT,
                    no_wa               VARCHAR(50) UNIQUE
                );
            """)

            # Add columns if they do not exist (MySQL logic using exception handling or skip since it's hard without SP)
            # In MySQL, we just suppress errors for ALTER TABLE if columns exist.
            try:
                cur.execute("ALTER TABLE teachers ADD COLUMN no_wa VARCHAR(50) UNIQUE;")
            except Exception: pass

            try:
                cur.execute("ALTER TABLE teachers ADD COLUMN min_jp INT DEFAULT 2;")
                cur.execute("ALTER TABLE teachers ADD COLUMN max_jp INT DEFAULT 60;")
                cur.execute("ALTER TABLE teachers ADD COLUMN allowed_jp_pagi TEXT;")
                cur.execute("ALTER TABLE teachers ADD COLUMN allowed_jp_siang TEXT;")
                cur.execute("ALTER TABLE teachers DROP COLUMN ideal_min_jp;")
                cur.execute("ALTER TABLE teachers DROP COLUMN ideal_max_jp;")
                cur.execute("ALTER TABLE teachers DROP COLUMN max_jp_mutlak;")
            except Exception: pass

            cur.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id_kelas          INT AUTO_INCREMENT PRIMARY KEY,
                    nama_kelas        VARCHAR(100) UNIQUE NOT NULL,
                    shift_operasional VARCHAR(10) CHECK (shift_operasional IN ('PAGI','SIANG')),
                    tingkat           VARCHAR(50),
                    jurusan           VARCHAR(100)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id_mapel       INT AUTO_INCREMENT PRIMARY KEY,
                    nama_mapel     VARCHAR(200) NOT NULL,
                    kategori_mapel VARCHAR(100),
                    tingkat        VARCHAR(50),
                    jurusan        VARCHAR(100)
                );
            """)

            try:
                cur.execute("ALTER TABLE classes ADD COLUMN tingkat VARCHAR(50);")
                cur.execute("ALTER TABLE classes ADD COLUMN jurusan VARCHAR(100);")
                cur.execute("ALTER TABLE subjects ADD COLUMN tingkat VARCHAR(50);")
                cur.execute("ALTER TABLE subjects ADD COLUMN jurusan VARCHAR(100);")
            except Exception: pass

            cur.execute("""
                CREATE TABLE IF NOT EXISTS teacher_subjects (
                    id_teacher_subject INT AUTO_INCREMENT PRIMARY KEY,
                    id_guru            INT,
                    id_mapel           INT,
                    UNIQUE(id_guru, id_mapel),
                    FOREIGN KEY (id_guru) REFERENCES teachers(id_guru) ON DELETE CASCADE,
                    FOREIGN KEY (id_mapel) REFERENCES subjects(id_mapel) ON DELETE CASCADE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS class_subjects (
                    id_class_subject INT AUTO_INCREMENT PRIMARY KEY,
                    id_kelas         INT,
                    id_mapel         INT,
                    durasi_jp        INT NOT NULL,
                    id_guru_mutlak   INT,
                    UNIQUE(id_kelas, id_mapel),
                    FOREIGN KEY (id_kelas) REFERENCES classes(id_kelas) ON DELETE CASCADE,
                    FOREIGN KEY (id_mapel) REFERENCES subjects(id_mapel) ON DELETE CASCADE,
                    FOREIGN KEY (id_guru_mutlak) REFERENCES teachers(id_guru) ON DELETE SET NULL
                );
            """)

            try:
                cur.execute("ALTER TABLE class_subjects ADD COLUMN id_guru_mutlak INT;")
                cur.execute("ALTER TABLE class_subjects ADD FOREIGN KEY (id_guru_mutlak) REFERENCES teachers(id_guru) ON DELETE SET NULL;")
            except Exception: pass

            cur.execute("""
                CREATE TABLE IF NOT EXISTS timetable (
                    id_timetable     INT AUTO_INCREMENT PRIMARY KEY,
                    id_class_subject INT,
                    hari             VARCHAR(20) NOT NULL,
                    jam_ke           INT NOT NULL,
                    id_guru          INT,
                    is_fallback      TINYINT(1) DEFAULT 0,
                    original_guru_id INT,
                    FOREIGN KEY (id_class_subject) REFERENCES class_subjects(id_class_subject) ON DELETE CASCADE,
                    FOREIGN KEY (id_guru) REFERENCES teachers(id_guru) ON DELETE SET NULL,
                    FOREIGN KEY (original_guru_id) REFERENCES teachers(id_guru) ON DELETE SET NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    `key`   VARCHAR(100) PRIMARY KEY,
                    `value` TEXT NOT NULL
                );
            """)

            conn.commit()
            logger.info(f"Schema MySQL untuk cabang '{branch}' berhasil diinisialisasi.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Gagal menginisialisasi database cabang '{branch}': {e}")
            raise e
        finally:
            cur.close()
            conn.close()
            active_branch.reset(token)

    # Migrasi data tidak diperlukan lagi karena beda engine. 
    # migrate_public_to_bekasi() ditiadakan.


# ─────────────────────────────────────────────
# Settings helpers
# ─────────────────────────────────────────────

def save_setting(key: str, value: str):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO system_settings (`key`, `value`) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)",
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
        cur.execute("SELECT `value` FROM system_settings WHERE `key` = %s", (key,))
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
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cur.execute("TRUNCATE TABLE timetable;")
        cur.execute("TRUNCATE TABLE class_subjects;")
        cur.execute("TRUNCATE TABLE teacher_subjects;")
        cur.execute("TRUNCATE TABLE teachers;")
        cur.execute("TRUNCATE TABLE classes;")
        cur.execute("TRUNCATE TABLE subjects;")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
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
    print("Database MySQL berhasil diinisialisasi.")
