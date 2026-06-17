"""
seeder.py — Mengisi data master guru, mata pelajaran, dan relasi guru-mapel
ke database Supabase (PostgreSQL).

Jalankan dengan:
    py -m backend.seeder

Seeder ini bersifat IDEMPOTENT:
  - Guru   → INSERT ON CONFLICT (kode_guru) DO NOTHING
  - Mapel  → INSERT ON CONFLICT (nama_mapel) DO NOTHING
  - Relasi → INSERT ON CONFLICT (id_guru, id_mapel) DO NOTHING
  - Tidak menghapus data yang sudah ada.
"""

import os
import re
import json
import logging
from dotenv import load_dotenv

def parse_allocations() -> list[dict]:
    """Parse the markdown file '# DATA ALOKASI JAM PELAJARAN (JP) PER KE.md' to extract class allocations.
    Returns a list of dicts: {'class': str, 'subject': str, 'jp': int}
    """
    allocations = []
    md_path = os.path.join(os.path.dirname(__file__), "# DATA ALOKASI JAM PELAJARAN (JP) PER KE.md")
    if not os.path.exists(md_path):
        logger.error(f"File alokasi tidak ditemukan: {md_path}")
        return allocations
    current_classes = []
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Detect class heading e.g., '### X AK 1' or '### XII OTKP 1 & XII OTKP 2 (Masing-Masing Kelas)'
            if line.startswith("###"):
                heading_content = line[3:].strip()
                # Remove "(Masing-Masing Kelas)" if present
                heading_content = re.sub(r"\(masing-masing kelas\)", "", heading_content, flags=re.IGNORECASE).strip()
                # Split by commas, ampersands, or "dan" / "and"
                parts = re.split(r"[\,\&]|(?:\s+dan\s+)|(?:\s+and\s+)", heading_content, flags=re.IGNORECASE)
                current_classes = [p.strip() for p in parts if p.strip()]
                continue
            # Detect subject lines like '* Matematika: **5 JP**'
            subject_match = re.match(r"^\*\s+([^:]+):\s+\*\*([0-9]+) JP\*\*", line)
            if subject_match and current_classes:
                subject = subject_match.group(1).strip()
                jp = int(subject_match.group(2))
                for cname in current_classes:
                    allocations.append({"class": cname, "subject": subject, "jp": jp})
    return allocations
from backend.database import get_db_connection, db_fetchone, db_execute

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# KATEGORISASI MAPEL
# Referensi: SYSTEM_BLUEPRINT.md §2.C
#   UMUM      = mapel normatif / adaptif (Matematika, B.Indo, dsb.)
#   OLAHRAGA  = Penjasorkes / PJOK
#   PRODUKTIF = mapel kejuruan / vokasi
# ──────────────────────────────────────────────────────────────

UMUM = "UMUM"
OLAHRAGA = "OLAHRAGA"
PRODUKTIF = "PRODUKTIF"

# ──────────────────────────────────────────────────────────────
# DATA MATA PELAJARAN (unik, setelah normalisasi nama)
# ──────────────────────────────────────────────────────────────

SUBJECTS: list[dict] = [
    # ── UMUM ─────────────────────────────────────────────────
    {"nama_mapel": "Matematika",                         "kategori_mapel": UMUM},
    {"nama_mapel": "Bahasa Indonesia",                   "kategori_mapel": UMUM},
    {"nama_mapel": "Bahasa Inggris",                     "kategori_mapel": UMUM},
    {"nama_mapel": "PPKn",                               "kategori_mapel": UMUM},
    {"nama_mapel": "PKK",                                "kategori_mapel": UMUM},
    {"nama_mapel": "Sejarah Indonesia",                  "kategori_mapel": UMUM},
    {"nama_mapel": "Etika Profesi",                      "kategori_mapel": UMUM},
    {"nama_mapel": "Seni Budaya",                        "kategori_mapel": UMUM},
    {"nama_mapel": "Pendidikan Agama Islam",             "kategori_mapel": UMUM},
    {"nama_mapel": "Informatika",                        "kategori_mapel": UMUM},
    {"nama_mapel": "IPAS",                               "kategori_mapel": UMUM},

    # ── OLAHRAGA ──────────────────────────────────────────────
    {"nama_mapel": "Penjasorkes",                        "kategori_mapel": OLAHRAGA},

    # ── PRODUKTIF — Akuntansi & Keuangan Lembaga (AKL) ───────
    {"nama_mapel": "Akuntansi Dasar",                    "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur",
                                                         "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Keuangan",                       "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Lembaga",                         "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Ekonomi Bisnis",                     "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Keuangan",                        "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Komputer Akuntansi",                 "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Spreadsheet",                        "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Perbankan Dasar",                    "kategori_mapel": PRODUKTIF},

    # ── PRODUKTIF — OTKP (Otomatisasi dan Tata Kelola Perkantoran) ──
    {"nama_mapel": "Korespondensi",                      "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Humas",                          "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Kepegawaian",                    "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Sarpras",                        "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Teknologi Perkantoran",              "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Kearsipan",                          "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm Pajak",                          "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm Umum",                           "kategori_mapel": PRODUKTIF},

    # ── PRODUKTIF — TKR (Teknik Kendaraan Ringan) ─────────────
    {"nama_mapel": "Kelistrikan Kendaraan",              "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Kelistrikan Kendaraan Ringan",       "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Kelistrikan Sepeda Motor",           "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Main. Mesin Sepeda Motor",           "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Main. Sasis Sepeda Motor",           "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Main. Mesin Kendaraan",              "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Main. Sasis Kendaraan",              "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "TDO",                                "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "PDTO",                               "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Gambar Teknik",                      "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "K3LH",                               "kategori_mapel": PRODUKTIF},

    # ── PRODUKTIF — TKJ (Teknik Komputer dan Jaringan) ────────
    {"nama_mapel": "Dasar Jaringan Komputer",            "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Wide Area Network (WAN)",             "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Teknik Infrastruktur Jaringan",      "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm Sistem Jaringan",                "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Jaringan Komputer",              "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Bisnis Teknologi Informasi",         "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Layanan Jaringan",               "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "KKA / Coding",                       "kategori_mapel": PRODUKTIF},
]

# ──────────────────────────────────────────────────────────────
# DATA GURU
# kode_guru: nomor urut dari data asli (1–37)
# hari_tersedia default: semua hari SENIN-SABTU (bisa diubah via UI)
# shift_pagi & shift_siang default: True (keduanya)
# ──────────────────────────────────────────────────────────────

ALL_DAYS = json.dumps(["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"])

def _guru(no: int, nama: str) -> dict:
    return {
        "kode_guru":           no,
        "nama_guru":           nama,
        "hari_tersedia":       ALL_DAYS,
        "shift_pagi":          True,
        "shift_siang":         True,
        "hari_tersedia_pagi":  ALL_DAYS,
        "hari_tersedia_siang": ALL_DAYS,
    }

TEACHERS: list[dict] = [
    _guru(1,  "REZA PATRIOTA PUTRA, S.Kom"),
    _guru(2,  "TAMAN SASTRA DIKARNA, S.Pd"),
    _guru(3,  "SUHARNO, S.Pdi"),
    _guru(4,  "SAMSUL HUDA, S.Pd"),
    _guru(5,  "AHMAD HUSEN NASUTION, SS"),
    _guru(6,  "WISNU NARA UTAMA, S.Pd"),
    _guru(7,  "FITRI MULYANI, S.Pd"),
    _guru(8,  "DERA ISMAWATI, S.PdI"),
    _guru(9,  "WIDONI SANTOSO, S.Pd"),
    _guru(10, "SRI TITA MULYATI"),
    _guru(11, "EUIS SUPRIHATIN, S.Pd"),
    _guru(12, "WIDA HARTANI, S.Pd"),
    _guru(13, "LUTHFI AHMAD NAZHIF, S.Pd"),
    _guru(14, "WIDJAYANTI, S.Sos"),
    _guru(15, "DEDE HIDAYATULLAH"),
    _guru(16, "KOKO"),
    _guru(17, "CHRISTIN SIREGAR, S.Pd"),
    _guru(18, "Muhammad Syafe'i"),
    _guru(19, "Muhammad Andika Prawira"),
    _guru(20, "Dra. Sri Chandri Yani"),
    _guru(21, "Yulistio"),
    _guru(22, "Kuat Suparto"),
    _guru(23, "Astri Wulandari"),
    _guru(24, "Arief Akbar Fadillah"),
    _guru(25, "Agung Ainul Hakim"),
    _guru(26, "Sutrisno"),
    _guru(27, "Muhammad Albar Sapin"),
    _guru(28, "Tiara Shanti Hartono, S.Sos"),
    _guru(29, "Oktari Qomimis Syatun, S.Pd"),
    _guru(30, "Catur Wulandari"),
    _guru(31, "Dwiana Rikasari, S.Ap"),
    _guru(32, "IDAYATUL MUSTAFIDAH"),
    _guru(33, "RISKA AMELIA, S.M"),
    _guru(34, "SISTER NINDA PUTRI, S.Pd"),
    _guru(35, "DELA AMELIA PUTRI, S.Pd"),
    _guru(36, "WIWIK UMAYAH, S.Pd"),
    _guru(37, "ENDANG KURNIAWAN, ST"),
]

# ──────────────────────────────────────────────────────────────
# RELASI GURU ↔ MATA PELAJARAN
# Format: { kode_guru: [nama_mapel, ...] }
# nama_mapel harus PERSIS sama dengan nama di SUBJECTS di atas.
# ──────────────────────────────────────────────────────────────

TEACHER_SUBJECTS: dict[int, list[str]] = {
    1:  [],  # REZA PATRIOTA PUTRA — tanpa mapel
    2:  ["Matematika"],
    3:  ["Penjasorkes"],
    4:  ["Matematika"],
    5:  ["PPKn"],
    6:  ["PKK"],
    7:  [
        "Akuntansi Dasar",
        "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur",
        "OTK Keuangan",
        "AK Lembaga",
        "Ekonomi Bisnis",
    ],
    8:  ["Korespondensi", "OTK Humas"],
    9:  ["Penjasorkes"],
    10: ["Penjasorkes"],
    11: ["Sejarah Indonesia", "Etika Profesi", "Perbankan Dasar", "PKK"],
    12: ["PPKn"],
    13: ["Bahasa Indonesia"],
    14: ["OTK Kepegawaian", "Adm Pajak"],
    15: ["Matematika"],
    16: [
        "Kelistrikan Kendaraan",
        "Main. Mesin Sepeda Motor",
        "TDO",
        "PDTO",
        "Main. Sasis Sepeda Motor",
        "Kelistrikan Sepeda Motor",
    ],
    17: ["Bahasa Inggris"],
    18: ["Pendidikan Agama Islam"],
    19: ["Teknik Infrastruktur Jaringan", "KKA / Coding", "Tek Layanan Jaringan"],
    20: ["Sejarah Indonesia"],
    21: [
        "Main. Mesin Kendaraan",
        "Main. Sasis Kendaraan",
        "PDTO",
        "TDO",
        "Main. Sasis Sepeda Motor",
        "Kelistrikan Kendaraan Ringan",
    ],
    22: ["Gambar Teknik", "TDO", "K3LH", "PDTO"],
    23: ["Bahasa Indonesia", "Spreadsheet", "AK Keuangan"],
    24: ["Pendidikan Agama Islam"],
    25: [
        "Dasar Jaringan Komputer",
        "Wide Area Network (WAN)",
        "Teknik Infrastruktur Jaringan",
        "Adm Sistem Jaringan",
        "Informatika",
    ],
    26: [
        "Tek Jaringan Komputer",
        "Bisnis Teknologi Informasi",
        "Tek Layanan Jaringan",
        "Wide Area Network (WAN)",
        "Informatika",
    ],
    27: ["Teknologi Perkantoran", "OTK Humas", "OTK Sarpras", "Kearsipan"],
    28: ["Bahasa Inggris"],
    29: ["PPKn", "Sejarah Indonesia"],
    30: ["Adm Umum", "IPAS"],
    31: [],  # Dwiana Rikasari — tanpa mapel
    32: ["Komputer Akuntansi"],
    33: ["Seni Budaya"],
    34: ["Bahasa Inggris"],
    35: ["Matematika"],
    36: ["Bahasa Indonesia"],
    37: ["TDO", "PDTO", "K3LH", "Main. Mesin Kendaraan"],
}


# ──────────────────────────────────────────────────────────────
# FUNGSI SEEDER
# ──────────────────────────────────────────────────────────────

def get_class_info(nama_kelas: str) -> tuple[str | None, str | None, str]:
    parts = nama_kelas.split()
    tingkat = None
    jurusan = None
    if len(parts) >= 2:
        tk = parts[0].upper()
        if tk in ("X", "XI", "XII"):
            tingkat = tk
            jurusan = parts[1].upper()
    
    # Determine shift
    if tingkat == "XI":
        shift = "SIANG"
    else:
        shift = "PAGI"
        
    return tingkat, jurusan, shift


def run_seeder():
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # ── 1. Tambah constraint unik pada subjects jika belum ada ─────
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'subjects_nama_mapel_key'
                ) THEN
                    ALTER TABLE subjects ADD CONSTRAINT subjects_nama_mapel_key UNIQUE (nama_mapel);
                END IF;
            END
            $$;
        """)

        # ── 2. Insert mata pelajaran ───────────────────────────────────
        logger.info("Memasukkan data mata pelajaran...")
        mapel_count = 0
        for s in SUBJECTS:
            cur.execute(
                """
                INSERT INTO subjects (nama_mapel, kategori_mapel)
                VALUES (%s, %s)
                ON CONFLICT (nama_mapel) DO NOTHING
                """,
                (s["nama_mapel"], s["kategori_mapel"]),
            )
            if cur.rowcount:
                mapel_count += 1
        logger.info(f"  → {mapel_count} mapel baru dimasukkan (dari {len(SUBJECTS)} total).")

        # ── 3. Bangun lookup nama_mapel → id_mapel ────────────────────
        cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
        mapel_map: dict[str, int] = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}

        # ── 4. Insert guru ────────────────────────────────────────────
        logger.info("Memasukkan data guru...")
        guru_count = 0
        for t in TEACHERS:
            cur.execute(
                """
                INSERT INTO teachers
                    (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang,
                     hari_tersedia_pagi, hari_tersedia_siang)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (kode_guru) DO NOTHING
                """,
                (
                    t["kode_guru"],
                    t["nama_guru"],
                    t["hari_tersedia"],
                    t["shift_pagi"],
                    t["shift_siang"],
                    t["hari_tersedia_pagi"],
                    t["hari_tersedia_siang"],
                ),
            )
            if cur.rowcount:
                guru_count += 1
        logger.info(f"  → {guru_count} guru baru dimasukkan (dari {len(TEACHERS)} total).")

        # ── 5. Bangun lookup kode_guru → id_guru ──────────────────────
        cur.execute("SELECT id_guru, kode_guru FROM teachers")
        guru_map: dict[int, int] = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}

        # ── 6. Insert relasi teacher_subjects ─────────────────────────
        logger.info("Memasukkan relasi guru ↔ mata pelajaran...")
        rel_count  = 0
        err_count  = 0
        for kode_guru, mapel_list in TEACHER_SUBJECTS.items():
            id_guru = guru_map.get(kode_guru)
            if id_guru is None:
                logger.warning(f"  ⚠ kode_guru={kode_guru} tidak ditemukan di DB, lewati.")
                continue
            for nama_mapel in mapel_list:
                id_mapel = mapel_map.get(nama_mapel)
                if id_mapel is None:
                    logger.error(
                        f"  ✗ Mapel '{nama_mapel}' (kode_guru={kode_guru}) "
                        f"tidak ada di tabel subjects!"
                    )
                    err_count += 1
                    continue
                cur.execute(
                    """
                    INSERT INTO teacher_subjects (id_guru, id_mapel)
                    VALUES (%s, %s)
                    ON CONFLICT (id_guru, id_mapel) DO NOTHING
                    """,
                    (id_guru, id_mapel),
                )
                if cur.rowcount:
                    rel_count += 1

        logger.info(f"  → {rel_count} relasi baru dimasukkan.")
        if err_count:
            logger.warning(f"  ⚠ {err_count} entri gagal karena nama mapel tidak cocok.")

        # ── 7. Insert classes based on allocation data ────────────────────────────────
        logger.info("Memasukkan data kelas dan alokasi JP...")
        
        # Clean up malformed classes first (classes with null shift or containing special characters)
        cur.execute("""
            DELETE FROM classes 
            WHERE shift_operasional IS NULL 
               OR nama_kelas LIKE '%&%' 
               OR nama_kelas LIKE '%,%' 
               OR nama_kelas LIKE '% DAN %' 
               OR nama_kelas LIKE '% AND %'
        """)
        
        allocations = parse_allocations()
        # Insert classes (unique)
        class_names = {alloc['class'] for alloc in allocations}
        for class_name in class_names:
            tingkat, jurusan, shift = get_class_info(class_name)
            cur.execute(
                """
                INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (nama_kelas) DO UPDATE SET
                    shift_operasional = EXCLUDED.shift_operasional,
                    tingkat = EXCLUDED.tingkat,
                    jurusan = EXCLUDED.jurusan
                """,
                (class_name, shift, tingkat, jurusan)
            )
        conn.commit()
        # Build lookup maps
        cur.execute("SELECT id_kelas, nama_kelas FROM classes")
        class_map = {row["nama_kelas"]: row["id_kelas"] for row in cur.fetchall()}
        cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
        subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
        # Insert class_subjects with durasi_jp
        for alloc in allocations:
            id_kelas = class_map.get(alloc['class'])
            id_mapel = subject_map.get(alloc['subject'])
            if id_kelas is None or id_mapel is None:
                logger.warning(f"⚠️ Alokasi gagal: kelas={alloc['class']} atau mapel={alloc['subject']} tidak ditemukan di DB")
                continue
            cur.execute(
                """
                INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_kelas, id_mapel) DO UPDATE SET durasi_jp = EXCLUDED.durasi_jp
                """,
                (id_kelas, id_mapel, alloc['jp'])
            )
        conn.commit()
        logger.info("✅ Alokasi kelas selesai.")

        logger.info("✅ Seeding selesai!")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Seeding gagal: {e}")
        raise
    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_seeder()
