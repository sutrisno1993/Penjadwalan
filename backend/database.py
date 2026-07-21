"""
database.py — Koneksi dan inisialisasi schema ke MySQL
"""
import os
import logging
import threading
from contextvars import ContextVar
import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB

logger = logging.getLogger(__name__)

# ContextVar untuk menyimpan cabang/skema aktif (bekasi atau jakarta)
# Di-backup dengan thread-local storage untuk endpoint sinkron FastAPI (threadpool)
active_branch: ContextVar[str] = ContextVar("active_branch", default="bekasi")

# Thread-local storage sebagai fallback untuk sync endpoints di threadpool
_thread_local = threading.local()

def set_thread_branch(branch: str):
    """Set branch di thread-local storage (untuk sync FastAPI endpoints)."""
    _thread_local.branch = branch

def get_thread_branch() -> str:
    """Get branch dari thread-local, fallback ke ContextVar."""
    return getattr(_thread_local, "branch", None) or active_branch.get("bekasi")


# ─────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────

def _get_db_config():
    """
    Membaca konfigurasi database dari environment (.env).
    """
    host     = os.environ.get("DB_HOST", "127.0.0.1").strip()
    port     = int(os.environ.get("DB_PORT", "3306").strip())
    user     = os.environ.get("DB_USER", "root").strip()
    password = os.environ.get("DB_PASSWORD", "").strip()
    db_name  = os.environ.get("DB_NAME", "jadwal_bekasi").strip()

    url = os.environ.get("DATABASE_URL", "").strip()
    if url and url.startswith("mysql"):
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(url.replace("mysql+pymysql://", "mysql://"))
        host = parsed.hostname or host
        port = parsed.port or port
        user = parsed.username or user
        password = parsed.password or password
        if parsed.path and len(parsed.path.strip("/")) > 0:
            db_name = parsed.path.strip("/")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": db_name
    }

def get_current_db_name() -> str:
    return _get_db_config()["database"]

def get_branch_name() -> str:
    db_name = get_current_db_name()
    if db_name.startswith("jadwal_"):
        raw = db_name.replace("jadwal_", "").replace("_", " ")
        return raw.title()
    return db_name.title()


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

def get_db_connection(auto_create_db=False, branch: str = None):
    """Mengembalikan koneksi MySQL ke database yang dikonfigurasi di .env."""
    global _connection_pool
    config = _get_db_config()
    db_name = config["database"]

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
    """Membuat semua tabel jika belum ada di database yang dikonfigurasi di .env."""
    db_name = get_current_db_name()
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

        # Add columns if they do not exist
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

        cur.execute("""
            CREATE TABLE IF NOT EXISTS lms_endpoints (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                title        VARCHAR(255) NOT NULL,
                url          VARCHAR(500) NOT NULL,
                secret_token VARCHAR(255) DEFAULT '',
                is_active    TINYINT(1) DEFAULT 0,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS time_slots (
                id_slot      INT AUTO_INCREMENT PRIMARY KEY,
                hari         VARCHAR(20) NOT NULL,
                shift        VARCHAR(10) NOT NULL DEFAULT 'PAGI',
                jam_ke       INT NULL,
                tipe_slot    VARCHAR(50) NOT NULL DEFAULT 'KBM',
                jam_mulai    VARCHAR(10) NOT NULL,
                jam_selesai  VARCHAR(10) NOT NULL,
                keterangan   VARCHAR(100) NULL,
                urutan       INT DEFAULT 0
            );
        """)

        # Inisialisasi default time slots jika tabel kosong
        cur.execute("SELECT COUNT(*) as cnt FROM time_slots;")
        row_cnt = cur.fetchone()
        if not row_cnt or row_cnt.get('cnt', 0) == 0:
            _seed_default_time_slots(cur)

        conn.commit()
        logger.info(f"Schema MySQL untuk database '{db_name}' berhasil diinisialisasi.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Gagal menginisialisasi database '{db_name}': {e}")
        raise e
    finally:
        cur.close()
        conn.close()

    # Migrasi data tidak diperlukan lagi karena beda engine. 
    # migrate_public_to_bekasi() ditiadakan.


def _seed_default_time_slots(cur):
    """Memasukkan data awal alokasi waktu jam pelajaran (Default Bell Schedule)."""
    default_slots = []
    
    # ── SHIFT PAGI ──
    # SENIN
    default_slots.append(('SENIN', 'PAGI', None, 'UPACARA', '06:30', '07:30', 'Upacara Bendera', 1))
    default_slots.append(('SENIN', 'PAGI', 1, 'KBM', '07:30', '08:10', 'Jam Ke-1', 2))
    default_slots.append(('SENIN', 'PAGI', 2, 'KBM', '08:10', '08:50', 'Jam Ke-2', 3))
    default_slots.append(('SENIN', 'PAGI', 3, 'KBM', '08:50', '09:30', 'Jam Ke-3', 4))
    default_slots.append(('SENIN', 'PAGI', None, 'ISTIRAHAT', '09:30', '10:00', 'Istirahat', 5))
    default_slots.append(('SENIN', 'PAGI', 4, 'KBM', '10:00', '10:35', 'Jam Ke-4', 6))
    default_slots.append(('SENIN', 'PAGI', 5, 'KBM', '10:35', '11:10', 'Jam Ke-5', 7))
    default_slots.append(('SENIN', 'PAGI', 6, 'KBM', '11:10', '11:45', 'Jam Ke-6', 8))
    default_slots.append(('SENIN', 'PAGI', 7, 'KBM', '11:45', '12:20', 'Jam Ke-7', 9))

    # SELASA, RABU, KAMIS (Regular days)
    for hari in ['SELASA', 'RABU', 'KAMIS']:
        default_slots.append((hari, 'PAGI', 1, 'KBM', '07:00', '07:45', 'Jam Ke-1', 1))
        default_slots.append((hari, 'PAGI', 2, 'KBM', '07:45', '08:30', 'Jam Ke-2', 2))
        default_slots.append((hari, 'PAGI', 3, 'KBM', '08:30', '09:15', 'Jam Ke-3', 3))
        default_slots.append((hari, 'PAGI', 4, 'KBM', '09:15', '10:00', 'Jam Ke-4', 4))
        default_slots.append((hari, 'PAGI', None, 'ISTIRAHAT', '10:00', '10:30', 'Istirahat', 5))
        default_slots.append((hari, 'PAGI', 5, 'KBM', '10:30', '11:15', 'Jam Ke-5', 6))
        default_slots.append((hari, 'PAGI', 6, 'KBM', '11:15', '12:00', 'Jam Ke-6', 7))
        default_slots.append((hari, 'PAGI', 7, 'KBM', '12:00', '12:45', 'Jam Ke-7', 8))

    # JUMAT
    default_slots.append(('JUMAT', 'PAGI', 1, 'KBM', '07:00', '07:40', 'Jam Ke-1', 1))
    default_slots.append(('JUMAT', 'PAGI', 2, 'KBM', '07:40', '08:20', 'Jam Ke-2', 2))
    default_slots.append(('JUMAT', 'PAGI', 3, 'KBM', '08:20', '09:00', 'Jam Ke-3', 3))
    default_slots.append(('JUMAT', 'PAGI', 4, 'KBM', '09:00', '09:40', 'Jam Ke-4', 4))
    default_slots.append(('JUMAT', 'PAGI', None, 'ISTIRAHAT', '09:40', '10:10', 'Istirahat / Sholat', 5))
    default_slots.append(('JUMAT', 'PAGI', 5, 'KBM', '10:10', '10:50', 'Jam Ke-5', 6))
    default_slots.append(('JUMAT', 'PAGI', 6, 'KBM', '10:50', '11:30', 'Jam Ke-6', 7))

    # SABTU
    default_slots.append(('SABTU', 'PAGI', 1, 'KBM', '07:00', '07:40', 'Jam Ke-1', 1))
    default_slots.append(('SABTU', 'PAGI', 2, 'KBM', '07:40', '08:20', 'Jam Ke-2', 2))
    default_slots.append(('SABTU', 'PAGI', 3, 'KBM', '08:20', '09:00', 'Jam Ke-3', 3))
    default_slots.append(('SABTU', 'PAGI', 4, 'KBM', '09:00', '09:40', 'Jam Ke-4', 4))

    # ── SHIFT SIANG ──
    for hari in ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']:
        default_slots.append((hari, 'SIANG', 1, 'KBM', '13:00', '13:40', 'Jam Ke-1', 1))
        default_slots.append((hari, 'SIANG', 2, 'KBM', '13:40', '14:20', 'Jam Ke-2', 2))
        default_slots.append((hari, 'SIANG', 3, 'KBM', '14:20', '15:00', 'Jam Ke-3', 3))
        default_slots.append((hari, 'SIANG', None, 'ISTIRAHAT', '15:00', '15:30', 'Istirahat / Sholat', 4))
        default_slots.append((hari, 'SIANG', 4, 'KBM', '15:30', '16:10', 'Jam Ke-4', 5))
        default_slots.append((hari, 'SIANG', 5, 'KBM', '16:10', '16:50', 'Jam Ke-5', 6))
        default_slots.append((hari, 'SIANG', 6, 'KBM', '16:50', '17:30', 'Jam Ke-6', 7))

    cur.executemany(
        "INSERT INTO time_slots (hari, shift, jam_ke, tipe_slot, jam_mulai, jam_selesai, keterangan, urutan) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        default_slots
    )


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
# LMS Endpoint helpers
# ─────────────────────────────────────────────

def get_all_lms_endpoints() -> list:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT * FROM lms_endpoints ORDER BY is_active DESC, id ASC")
        return list(cur.fetchall())
    finally:
        cur.close()
        conn.close()


def create_lms_endpoint(nama_label: str, endpoint_url: str, bearer_token: str, keterangan: str = "") -> dict:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO lms_endpoints (nama_label, endpoint_url, bearer_token, keterangan) "
            "VALUES (%s, %s, %s, %s)",
            (nama_label, endpoint_url, bearer_token, keterangan or "")
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM lms_endpoints WHERE id = %s", (new_id,))
        return dict(cur.fetchone())
    finally:
        cur.close()
        conn.close()


def update_lms_endpoint(endpoint_id: int, nama_label: str, endpoint_url: str,
                         bearer_token: str = None, keterangan: str = "") -> bool:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        if bearer_token:
            cur.execute(
                "UPDATE lms_endpoints SET nama_label=%s, endpoint_url=%s, bearer_token=%s, keterangan=%s WHERE id=%s",
                (nama_label, endpoint_url, bearer_token, keterangan or "", endpoint_id)
            )
        else:
            cur.execute(
                "UPDATE lms_endpoints SET nama_label=%s, endpoint_url=%s, keterangan=%s WHERE id=%s",
                (nama_label, endpoint_url, keterangan or "", endpoint_id)
            )
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_lms_endpoint(endpoint_id: int) -> bool:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("DELETE FROM lms_endpoints WHERE id = %s", (endpoint_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def set_active_lms_endpoint(endpoint_id: int) -> bool:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("UPDATE lms_endpoints SET is_active = 0")
        cur.execute("UPDATE lms_endpoints SET is_active = 1 WHERE id = %s", (endpoint_id,))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


def get_active_lms_endpoint() -> dict | None:
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SELECT * FROM lms_endpoints WHERE is_active = 1 LIMIT 1")
        row = cur.fetchone()
        return dict(row) if row else None
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
