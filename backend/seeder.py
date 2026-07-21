"""
seeder.py — Mengisi data master guru, mata pelajaran, dan relasi guru-mapel
ke database Supabase (PostgreSQL).

Jalankan dengan:
    python -m backend.seeder

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
        
    # Subject name normalizations
    subject_map = {
        "Pendidikan Agama dan Budi Pekerti": "Pendidikan Agama Islam",
        "Pend Agama Islam": "Pendidikan Agama Islam",
        "Pendidikan Pancasila dan Kewarganegaraan": "PPKn",
        "Pendidikan Jasmani, Olah Raga & Kesehatan": "Penjasorkes",
        "AK Manufaktur": "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur",
        "Tek Insfrs Jaringan": "Teknik Infrastruktur Jaringan",
        "Teknologi Infrastruktur Jaringan": "Teknik Infrastruktur Jaringan",
        "Teknologi Layanan Jaringan": "Tek Layanan Jaringan",
        "Administrasi Sistem Jaringan": "Adm Sistem Jaringan",
        "WAN": "Wide Area Network (WAN)",
        "BAHASA INGGRIS": "Bahasa Inggris",
        "Informatik": "Informatika",
        "Sejarah": "Sejarah Indonesia",
    }
    
    # Class name normalizations
    class_map = {
        "X AK 1": "X AKL 1",
        "XI AK 1": "XI AKL 1",
        "XII AK 1": "XII AKL 1",
        "X TKR 1": "X TKRO 1",
        "X TKR 2": "X TKRO 2",
        "XI TKR 1": "XI TKRO 1",
        "XI TKR 2": "XI TKRO 2",
        "XII TKR 1": "XII TKRO 1",
        "XII TKR 2": "XII TKRO 2",
        "X TSM 1": "X TBSM 1",
        "X TSM 2": "X TBSM 2",
        "XI TSM 1": "XI TBSM 1",
        "XI TSM 2": "XI TBSM 2",
        "XII TSM 1": "XII TBSM 1",
        "XII TSM 2": "XII TBSM 2",
    }

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
                
                # Apply normalization
                subject = subject_map.get(subject, subject)
                
                for cname in current_classes:
                    cname = class_map.get(cname, cname)
                    # Skip XI TKRO 2 since it does not exist in PDF
                    if cname in ("XI TKR 2", "XI TKRO 2"):
                        continue
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

SUBJECTS_BEKASI: list[dict] = [
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
    {"nama_mapel": "KKA / Coding",                       "kategori_mapel": UMUM},

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
]

SUBJECTS_JAKARTA: list[dict] = [
    {"nama_mapel": "Accurate", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm Sistem Jaringan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm Umum", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Adm. Pajak", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Dasar", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Keuangan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Lembaga", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "AK Manufaktur", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Bahasa Indonesia", "kategori_mapel": UMUM},
    {"nama_mapel": "Bahasa Inggris", "kategori_mapel": UMUM},
    {"nama_mapel": "Bisnis Tek Informasi", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Dasar Komp Jaringan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Ekonomi Bisnis", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Etika Profesi", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Informatika", "kategori_mapel": UMUM},
    {"nama_mapel": "IPAS", "kategori_mapel": UMUM},
    {"nama_mapel": "K3LH", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Kearsipan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Korespondensi", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Komputer Akuntansi", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Matematika", "kategori_mapel": UMUM},
    {"nama_mapel": "OTK Humas", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Kepegawaian", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Keuangan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "OTK Sarpras", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "PAI", "kategori_mapel": UMUM},
    {"nama_mapel": "Pend. Agama Islam", "kategori_mapel": UMUM},
    {"nama_mapel": "Pend. Agama Kristen", "kategori_mapel": UMUM},
    {"nama_mapel": "Penjasorkes", "kategori_mapel": OLAHRAGA},
    {"nama_mapel": "Perbankan Dasar", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Photoshop / Editing", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "PKK", "kategori_mapel": UMUM},
    {"nama_mapel": "PPKn", "kategori_mapel": UMUM},
    {"nama_mapel": "Sejarah", "kategori_mapel": UMUM},
    {"nama_mapel": "Seni Budaya", "kategori_mapel": UMUM},
    {"nama_mapel": "Spreadsheet", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Insfr Jaringan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Jaringan Komp", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Layanan Jaringan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Tek Perkantoran", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "Teknologi Layanan Jaringan", "kategori_mapel": PRODUKTIF},
    {"nama_mapel": "WAN", "kategori_mapel": PRODUKTIF}
]

# Aliases for backwards compatibility with scratch scripts
SUBJECTS = SUBJECTS_BEKASI

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
        "no_wa":               f"08123456{no:04d}",
    }

def _guru_avail(no: int, nama: str, pagi_days: list[str], siang_days: list[str]) -> dict:
    shift_pagi = len(pagi_days) > 0
    shift_siang = len(siang_days) > 0
    union_days = sorted(list(set(pagi_days + siang_days)), key=lambda d: ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"].index(d))
    return {
        "kode_guru":           no,
        "nama_guru":           nama,
        "hari_tersedia":       json.dumps(union_days),
        "shift_pagi":          shift_pagi,
        "shift_siang":         shift_siang,
        "hari_tersedia_pagi":  json.dumps(pagi_days),
        "hari_tersedia_siang": json.dumps(siang_days),
        "no_wa":               f"08123456{no:04d}",
    }

from backend.database import active_branch

TEACHERS_BEKASI: list[dict] = [
    _guru_avail(1,  "REZA PATRIOTA PUTRA, S.Kom", [], []),
    _guru_avail(2,  "TAMAN SASTRA DIKARNA, S.Pd", ["SENIN", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(3,  "SUHARNO, S.Pdi", ["SELASA"], ["SELASA"]),
    _guru_avail(4,  "SAMSUL HUDA, S.Pd", ["SELASA", "RABU"], ["SELASA", "RABU"]),
    _guru_avail(5,  "AHMAD HUSEN NASUTION, SS", ["SENIN", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT"]),
    _guru_avail(6,  "WISNU NARA UTAMA, S.Pd", ["SELASA", "KAMIS", "SABTU"], ["SELASA", "KAMIS"]),
    _guru_avail(7,  "FITRI MULYANI, S.Pd", ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SELASA", "RABU", "KAMIS"]),
    _guru_avail(8,  "DERA ISMAWATI, S.PdI", ["SELASA", "RABU"], ["SELASA", "RABU"]),
    _guru_avail(9,  "WIDONI SANTOSO, S.Pd", ["RABU", "KAMIS"], ["RABU", "KAMIS"]),
    _guru_avail(10, "SRI TITA MULYATI", ["SENIN", "SELASA", "JUMAT", "SABTU"], ["SENIN", "SELASA", "JUMAT", "SABTU"]),
    _guru_avail(11, "EUIS SUPRIHATIN, S.Pd", ["SENIN", "SELASA", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "KAMIS", "JUMAT"]),
    _guru_avail(12, "WIDA HARTANI, S.Pd", ["SABTU"], ["SABTU"]),
    _guru_avail(13, "LUTHFI AHMAD NAZHIF, S.Pd", [], ["KAMIS"]),
    _guru_avail(14, "WIDJAYANTI, S.Sos", ["JUMAT", "SABTU"], ["JUMAT", "SABTU"]),
    _guru_avail(15, "DEDE HIDAYATULLAH", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "KAMIS", "JUMAT"]),
    _guru_avail(16, "KOKO, ST", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(17, "CHRISTIN SIREGAR, S.Pd", ["SELASA", "KAMIS", "JUMAT", "SABTU"], ["SELASA", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(18, "MUHAMMAD SYAFE'I", ["SENIN", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(19, "MUHAMMAD ANDIKA PRAWIRA, S.Kom", ["SENIN", "RABU", "JUMAT"], ["SENIN", "RABU", "JUMAT"]),
    _guru_avail(20, "YULISTIO HARDIYANTO, ST", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(21, "KUAT SUPARTO, ST", ["SELASA", "RABU", "SABTU"], ["SELASA", "RABU", "SABTU"]),
    _guru_avail(22, "ASTRI WULANDARI, S.Ak", ["SELASA", "KAMIS", "JUMAT", "SABTU"], ["SELASA", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(23, "AGUNG AINUL HAKIM", ["SENIN", "KAMIS", "SABTU"], ["SENIN", "KAMIS", "SABTU"]),
    _guru_avail(24, "SUTRISNO", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(25, "MUHAMMAD ALBAR SAPIN", ["SENIN", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT"]),
    _guru_avail(26, "TIARA SHANTI HARTONO, S.Sos", ["SELASA", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS"]),
    _guru_avail(27, "OKTARI QOMIMIS SYATUN, S.Pd", ["SENIN", "SELASA", "RABU", "SABTU"], ["SENIN", "SELASA", "RABU", "SABTU"]),
    _guru_avail(28, "CATUR WULANDARI, A.Md", ["SENIN", "SELASA", "RABU", "KAMIS", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(29, "DWIANA RIKASARI, S.Ap", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(30, "IDAYATUL MUSTAFIDAH", ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(31, "RISKA AMELIA, S.M", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(32, "SISTER NINDA PUTRI, S.Pd", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "KAMIS"]),
    _guru_avail(33, "DELA AMELIA PUTRI, S.Pd", ["SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(34, "WIWIK UMAYAH, S.Pd", ["SELASA", "RABU", "KAMIS", "JUMAT"], ["SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(35, "ENDANG KURNIAWAN, ST", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(36, "SEPTIANI RAKA SIWI, M.Pd", ["SABTU"], ["SABTU"]),
    _guru_avail(37, "FAUZI, S.Kom", ["SELASA", "KAMIS"], ["SELASA", "KAMIS"]),
    _guru_avail(38, "AZMIRAL AZIS, S.Pd", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(39, "MUHAMMAD SYACHTIKO, S.Pd", ["RABU", "KAMIS"], ["RABU", "KAMIS"]),
]

TEACHERS_JAKARTA: list[dict] = [
    _guru_avail(1,  "REZA PATRIOTA PUTRA, S.Kom", [], []),
    _guru_avail(2,  "SAMSUL HUDA, S.Pd", ["SENIN", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(3,  "TAMAN SASTRA DIKARNA, S.Pd", ["SELASA", "RABU"], ["SELASA", "RABU"]),
    _guru_avail(4,  "SUHARNO, S.Pdi", ["SENIN", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(5,  "WIDJAYANTI, S.Sos", ["SENIN", "SELASA", "RABU", "KAMIS"], ["SENIN", "SELASA", "RABU", "KAMIS"]),
    _guru_avail(6,  "WISNU NARA UTAMA, S.Pd", ["SENIN", "RABU", "JUMAT"], ["SENIN", "RABU", "JUMAT"]),
    _guru_avail(7,  "KHOIRIYAH, S.Ag", ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS"]),
    _guru_avail(8,  "RADEN HAZAIRIN, S.Pd", ["SABTU"], []),
    _guru_avail(9,  "YUNITA, S.Pd", ["SABTU"], ["SABTU"]),
    _guru_avail(10, "M. IMRON ROSYADI, S.Ag", ["SENIN", "SELASA", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "KAMIS", "JUMAT"]),
    _guru_avail(11, "DEWI PERIYANTI, S.P", ["SENIN", "SELASA", "RABU", "JUMAT"], ["SENIN", "SELASA", "RABU", "JUMAT"]),
    _guru_avail(12, "WIDONI SANTOSO, S.Pd", ["SENIN", "SELASA", "JUMAT", "SABTU"], ["SENIN", "SELASA", "JUMAT", "SABTU"]),
    _guru_avail(13, "EKA HERLINAH, SS", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"], ["SELASA", "RABU", "JUMAT", "SABTU"]),
    _guru_avail(14, "UMIDA SHOLIKATIN, S.Sos", ["SENIN", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(15, "DERA ISMAWATI, S.PdI", ["SENIN", "KAMIS"], ["SENIN", "KAMIS"]),
    _guru_avail(16, "M. ANDIKA PRAWIRA, S.Kom", ["SELASA", "KAMIS", "SABTU"], ["SELASA", "KAMIS", "SABTU"]),
    _guru_avail(17, "LIS WIDIA, S.Pd", [], ["SELASA", "RABU", "KAMIS", "SABTU"]),
    _guru_avail(18, "NAAFI WULANDARI, S.Pd", ["SENIN", "SELASA", "RABU", "JUMAT"], ["SELASA", "RABU"]),
    _guru_avail(19, "APIAN CANDRA ADITYA, S.Kom", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(20, "SUTIYARTI, S.PdI", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(21, "APRILIA DWI KARINA, S.Pd", ["SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(22, "AYU DESTIANI NURCAHYA, S.Pd", ["SELASA", "RABU", "KAMIS", "JUMAT"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]),
    _guru_avail(23, "MARSAULINAH, S.Kom", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"], []),
    _guru_avail(24, "SRI TITA MULYATI", ["RABU", "KAMIS"], ["RABU", "KAMIS"]),
    _guru_avail(25, "LELIYANI, SE", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(26, "TINANDAR HERMAWAN", ["SELASA", "KAMIS"], ["SELASA", "KAMIS"]),
    _guru_avail(27, "RIZKI YUNIJAR, A.Md", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(28, "SUTRISNO", [], ["SELASA", "RABU"]),
    _guru_avail(29, "KUAT SUPARTO, ST", ["KAMIS", "JUMAT"], ["SENIN", "KAMIS", "JUMAT"]),
    _guru_avail(30, "SHERLI IKA SUSANTI, S.Pd", ["SENIN", "SELASA", "JUMAT", "SABTU"], ["SENIN", "SELASA", "RABU", "JUMAT", "SABTU"]),
    _guru_avail(31, "SOFIANA NAZWA, S.Pd", ["SENIN", "SELASA", "RABU", "KAMIS", "SABTU"], ["SENIN", "SELASA", "RABU", "KAMIS", "SABTU"]),
    _guru_avail(32, "NUR ANNISA, S.Kom", ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"], ["SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]),
    _guru_avail(33, "MUHAMMAD SYAHTICKO, S.Pd", ["SENIN", "SELASA", "JUMAT", "SABTU"], ["SENIN", "SELASA", "JUMAT", "SABTU"]),
    _guru_avail(34, "FAUZI, S.Kom", ["SENIN", "RABU", "JUMAT", "SABTU"], ["SENIN", "RABU", "JUMAT", "SABTU"]),
    _guru(35, "ANGELA MARCELA"),
]

TEACHER_SUBJECTS_BEKASI: dict[int, list[str]] = {
    1:  [],  # REZA PATRIOTA PUTRA, S.Kom
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
    20: [
        "Main. Mesin Kendaraan",
        "Main. Sasis Kendaraan",
        "PDTO",
        "TDO",
        "Main. Sasis Sepeda Motor",
        "Kelistrikan Kendaraan Ringan",
    ],
    21: ["Gambar Teknik", "TDO", "K3LH", "PDTO"],
    22: ["Bahasa Indonesia", "Spreadsheet", "AK Keuangan"],
    23: [
        "Dasar Jaringan Komputer",
        "Wide Area Network (WAN)",
        "Teknik Infrastruktur Jaringan",
        "Adm Sistem Jaringan",
        "Informatika",
    ],
    24: [
        "Tek Jaringan Komputer",
        "Bisnis Teknologi Informasi",
        "Tek Layanan Jaringan",
        "Wide Area Network (WAN)",
        "Informatika",
    ],
    25: ["Teknologi Perkantoran", "OTK Humas", "OTK Sarpras", "Kearsipan"],
    26: ["Bahasa Inggris"],
    27: ["PPKn", "Sejarah Indonesia"],
    28: ["Adm Umum", "IPAS"],
    29: [],  # DWIANA RIKASARI, S.Ap
    30: ["Komputer Akuntansi"],
    31: ["Seni Budaya"],
    32: ["Bahasa Inggris"],
    33: ["Matematika"],
    34: ["Bahasa Indonesia"],
    35: ["TDO", "PDTO", "K3LH", "Main. Mesin Kendaraan"],
    36: [],  # SEPTIANI RAKA SIWI, M.Pd
    37: [],  # FAUZI, S.Kom
    38: [],  # AZMIRAL AZIS, S.Pd
    39: [],  # RAIHAN NABILA SYIFA, S.Pd
}

TEACHER_SUBJECTS_JAKARTA: dict[int, list[str]] = {
    1:  [],  # REZA PATRIOTA PUTRA, S.Kom
    2:  ["Matematika"],  # SAMSUL HUDA, S.Pd
    3:  ["Matematika"],  # TAMAN SASTRA DIKARNA, S.Pd
    4:  ["Penjasorkes"],  # SUHARNO, S.Pdi
    5:  [
        "OTK Humas", "Sejarah", "Adm Umum", "Korespondensi", "Ekonomi Bisnis",
        "Adm. Pajak", "OTK Keuangan"
    ],  # WIDJAYANTI, S.Sos
    6:  ["PKK"],  # WISNU NARA UTAMA, S.Pd
    7:  ["Bahasa Inggris"],  # KHOIRIYAH, S.Ag
    8:  ["PPKn"],  # RADEN HAZAIRIN, S.Pd
    9:  ["Accurate"],  # YUNITA, S.Pd
    10: ["PAI"],  # M. IMRON ROSYADI, S.Ag
    11: ["Matematika", "IPAS"],  # DEWI PERIYANTI, S.P
    12: ["Penjasorkes"],  # WIDONI SANTOSO, S.Pd
    13: ["Bahasa Inggris"],  # EKA HERLINAH, SS
    14: ["Seni Budaya", "Sejarah"],  # UMIDA SHOLIKATIN, S.Sos
    15: ["Korespondensi", "OTK Humas"],  # DERA ISMAWATI, S.PdI
    16: ["Teknologi Layanan Jaringan", "Tek Insfr Jaringan", "Adm Sistem Jaringan"],  # M. ANDIKA PRAWIRA, S.Kom
    17: ["Bahasa Inggris"],  # LIS WIDIA, S.Pd
    18: ["Matematika"],  # NAAFI WULANDARI, S.Pd
    19: ["Dasar Komp Jaringan", "Photoshop / Editing", "WAN", "Tek Insfr Jaringan"],  # APIAN CANDRA ADITYA, S.Kom
    20: ["Bahasa Indonesia", "Pend. Agama Islam"],  # SUTIYARTI, S.PdI
    21: ["PPKn", "AK Dasar", "Sejarah", "Perbankan Dasar", "PKK"],  # APRILIA DWI KARINA, S.Pd
    22: [
        "OTK Sarpras", "Adm Umum", "Kearsipan", "Tek Perkantoran", "AK Lembaga",
        "OTK Kepegawaian", "OTK Humas"
    ],  # AYU DESTIANI NURCAHYA, S.Pd
    23: ["Adm Sistem Jaringan", "Bisnis Tek Informasi"],  # MARSAULINAH, S.Kom
    24: ["Penjasorkes"],  # SRI TITA MULYATI
    25: ["AK Keuangan", "Ekonomi Bisnis", "AK Manufaktur"],  # LELIYANI, SE
    26: ["WAN", "Adm Sistem Jaringan", "Dasar Komp Jaringan", "Tek Jaringan Komp"],  # TINANDAR HERMAWAN
    27: ["Tek Perkantoran", "Adm Umum", "OTK Humas", "Etika Profesi", "PPKn"],  # RIZKI YUNIJAR, A.Md
    28: ["Adm Sistem Jaringan", "Tek Layanan Jaringan"],  # SUTRISNO
    29: ["K3LH"],  # KUAT SUPARTO, ST
    30: ["Bahasa Indonesia"],  # SHERLI IKA SUSANTI, S.Pd
    31: ["Matematika"],  # SOFIANA NAZWA, S.Pd
    32: ["Adm Sistem Jaringan", "Bisnis Tek Informasi", "Tek Layanan Jaringan"],  # NUR ANNISA, S.Kom
    33: ["Seni Budaya"],  # MUHAMMAD SYAHTICKO, S.Pd
    34: ["Informatika", "Spreadsheet"],  # FAUZI, S.Kom
    35: ["Pend. Agama Kristen"],  # ANGELA MARCELA
}

CLASSES_JAKARTA: list[tuple[str, str, str, str]] = [
    # (nama_kelas, shift_operasional, tingkat, jurusan)
    ("X AKL 1", "PAGI", "X", "AKL"),
    ("X OTKP 1", "PAGI", "X", "OTKP"),
    ("X OTKP 2", "PAGI", "X", "OTKP"),
    ("X OTKP 3", "SIANG", "X", "OTKP"),
    ("X OTKP 4", "SIANG", "X", "OTKP"),
    ("X TKJ 1", "PAGI", "X", "TKJ"),
    ("X TKJ 2", "PAGI", "X", "TKJ"),
    ("X TKJ 3", "SIANG", "X", "TKJ"),
    ("X TKJ 4", "SIANG", "X", "TKJ"),
    ("X TKJ 5", "SIANG", "X", "TKJ"),
    ("XI OTKP 1", "SIANG", "XI", "OTKP"),
    ("XI OTKP 2", "SIANG", "XI", "OTKP"),
    ("XI OTKP 3", "SIANG", "XI", "OTKP"),
    ("XI AKL 1", "SIANG", "XI", "AKL"),
    ("XI TKJ 1", "SIANG", "XI", "TKJ"),
    ("XI TKJ 2", "SIANG", "XI", "TKJ"),
    ("XI TKJ 3", "SIANG", "XI", "TKJ"),
    ("XI TKJ 4", "SIANG", "XI", "TKJ"),
    ("XII AK 1", "PAGI", "XII", "AKL"),
    ("XII OTKP 1", "PAGI", "XII", "OTKP"),
    ("XII OTKP 2", "PAGI", "XII", "OTKP"),
    ("XII TKJ 1", "PAGI", "XII", "TKJ"),
    ("XII TKJ 2", "PAGI", "XII", "TKJ"),
    ("XII TKJ 3", "PAGI", "XII", "TKJ"),
    ("XII TKJ 4", "PAGI", "XII", "TKJ"),
]

CURRICULA_JAKARTA: dict[str, dict[str, int]] = {
    "X AKL": {
        "Accurate": 2, "IPAS": 2, "Penjasorkes": 2, "Bahasa Inggris": 4, "Matematika": 5,
        "Bahasa Indonesia": 3, "Pend. Agama Islam": 2, "AK Dasar": 3, "Sejarah": 2,
        "Perbankan Dasar": 2, "Etika Profesi": 2, "PPKn": 2, "K3LH": 2, "Seni Budaya": 2,
        "Informatika": 3, "Spreadsheet": 2
    },
    "X OTKP": {
        "Bahasa Inggris": 4, "Adm Umum": 2, "Bahasa Indonesia": 3, "Informatika": 3,
        "IPAS": 2, "K3LH": 2, "Korespondensi": 3, "Matematika": 5, "OTK Humas": 3,
        "Pend. Agama Islam": 2, "Penjasorkes": 2, "PPKn": 2, "Sejarah": 2, "Seni Budaya": 2,
        "Tek Perkantoran": 3
    },
    "X TKJ": {
        "Bahasa Indonesia": 3, "IPAS": 2, "PAI": 2, "Penjasorkes": 2, "PPKn": 2, "Sejarah": 2,
        "Seni Budaya": 2, "Bisnis Tek Informasi": 3, "Informatika": 3, "K3LH": 3,
        "Tek Jaringan Komp": 3, "Bahasa Inggris": 4, "Dasar Komp Jaringan": 4, "Matematika": 5
    },
    "XI AKL": {
        "Komputer Akuntansi": 2, "Accurate": 2, "Adm Umum": 2, "Adm. Pajak": 2, "AK Keuangan": 2,
        "AK Lembaga": 2, "AK Manufaktur": 2, "Bahasa Inggris": 4, "Ekonomi Bisnis": 2,
        "Matematika": 5, "Pend. Agama Islam": 2, "Penjasorkes": 2, "Photoshop / Editing": 2,
        "PKK": 3, "PPKn": 2, "Sejarah": 2, "Seni Budaya": 2
    },
    "XI OTKP": {
        "Bahasa Indonesia": 3, "Bahasa Inggris": 4, "Kearsipan": 2, "Matematika": 5,
        "OTK Humas": 4, "OTK Kepegawaian": 2, "OTK Keuangan": 3, "OTK Sarpras": 2,
        "PAI": 2, "Penjasorkes": 2, "Photoshop / Editing": 2, "PKK": 3, "Sejarah": 2,
        "Seni Budaya": 2, "Pend. Agama Islam": 2
    },
    "XI TKJ": {
        "Adm Sistem Jaringan": 3, "Bahasa Indonesia": 3, "Bahasa Inggris": 4, "Matematika": 5,
        "PAI": 2, "Penjasorkes": 2, "Photoshop / Editing": 2, "PKK": 3, "PPKn": 2,
        "Sejarah": 2, "Seni Budaya": 2, "Tek Insfr Jaringan": 3, "Tek Layanan Jaringan": 4,
        "WAN": 3
    },
    "XII AKL": {
        "Accurate": 3, "Adm. Pajak": 2, "AK Keuangan": 2, "AK Lembaga": 2, "AK Manufaktur": 4,
        "Bahasa Indonesia": 3, "Bahasa Inggris": 4, "Ekonomi Bisnis": 2, "Matematika": 5,
        "PAI": 2, "Penjasorkes": 2, "PKK": 3, "PPKn": 2, "Sejarah": 2, "Seni Budaya": 2
    },
    "XII OTKP": {
        "Bahasa Inggris": 4, "Ekonomi Bisnis": 2, "Kearsipan": 2, "Matematika": 5,
        "OTK Humas": 4, "OTK Kepegawaian": 2, "OTK Keuangan": 3, "OTK Sarpras": 2,
        "Pend. Agama Islam": 2, "Penjasorkes": 2, "PKK": 3, "PPKn": 2, "Sejarah": 2,
        "Bahasa Indonesia": 3, "Seni Budaya": 2
    },
    "XII TKJ": {
        "Adm Sistem Jaringan": 4, "Bahasa Indonesia": 3, "Bahasa Inggris": 4, "Matematika": 5,
        "PAI": 2, "Penjasorkes": 2, "PKK": 3, "PPKn": 2, "Sejarah": 2, "Seni Budaya": 2,
        "Tek Insfr Jaringan": 4, "Teknologi Layanan Jaringan": 4, "WAN": 3
    }
}

# Aliases for backwards compatibility with scratch scripts
TEACHERS = TEACHERS_BEKASI
TEACHER_SUBJECTS = TEACHER_SUBJECTS_BEKASI


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


def run_seeder(target_branch: str = None):
    branch = (target_branch or active_branch.get("bekasi")).strip().lower()
    conn = get_db_connection(branch=branch)
    cur  = conn.cursor()
    try:
        # ── 1. Tambah constraint unik pada subjects jika belum ada ─────
        pass

        # ── 2. Insert mata pelajaran ───────────────────────────────────
        logger.info(f"Memasukkan data mata pelajaran untuk cabang '{branch}'...")
        if branch == "jakarta":
            subjects_list = SUBJECTS_JAKARTA
            logger.info("  -> Mengosongkan data mata pelajaran lama (Jakarta)...")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE timetable;")
            cur.execute("TRUNCATE TABLE class_subjects;")
            cur.execute("TRUNCATE TABLE teacher_subjects;")
            cur.execute("TRUNCATE TABLE subjects;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
        else:
            subjects_list = SUBJECTS_BEKASI

        mapel_count = 0
        for s in subjects_list:
            cur.execute(
                """
                INSERT IGNORE INTO subjects (nama_mapel, kategori_mapel)
                VALUES (%s, %s)
                """,
                (s["nama_mapel"], s["kategori_mapel"]),
            )
            if cur.rowcount:
                mapel_count += 1
        logger.info(f"  → {mapel_count} mapel baru dimasukkan (dari {len(subjects_list)} total).")

        # ── 3. Bangun lookup nama_mapel → id_mapel ────────────────────
        cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
        mapel_map: dict[str, int] = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}

        # ── 4. Clean up old teachers and insert guru ───────────────────────────────────
        logger.info("Membersihkan data guru lama yang tidak ada di seeder baru...")
        if branch == "jakarta":
            teachers_list = TEACHERS_JAKARTA
            teacher_subjects_dict = TEACHER_SUBJECTS_JAKARTA
        else:
            teachers_list = TEACHERS_BEKASI
            teacher_subjects_dict = TEACHER_SUBJECTS_BEKASI

        all_new_kodes = [t["kode_guru"] for t in teachers_list]
        placeholders = ", ".join(["%s"] * len(all_new_kodes))
        cur.execute(f"SELECT id_guru, nama_guru FROM teachers WHERE kode_guru NOT IN ({placeholders})", tuple(all_new_kodes))
        to_delete = cur.fetchall()
        if to_delete:
            delete_ids = [row["id_guru"] for row in to_delete]
            delete_names = [row["nama_guru"] for row in to_delete]
            logger.info(f"  → Menghapus guru lama: {', '.join(delete_names)}")
            id_placeholders = ", ".join(["%s"] * len(delete_ids))
            cur.execute(f"DELETE FROM teacher_subjects WHERE id_guru IN ({id_placeholders})", tuple(delete_ids))
            cur.execute(f"DELETE FROM teachers WHERE id_guru IN ({id_placeholders})", tuple(delete_ids))

        logger.info("Memasukkan data guru...")
        guru_count = 0
        for t in teachers_list:
            cur.execute(
                """
                INSERT INTO teachers
                    (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang,
                     hari_tersedia_pagi, hari_tersedia_siang, no_wa)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nama_guru = VALUES(nama_guru),
                    hari_tersedia = VALUES(hari_tersedia),
                    shift_pagi = VALUES(shift_pagi),
                    shift_siang = VALUES(shift_siang),
                    hari_tersedia_pagi = VALUES(hari_tersedia_pagi),
                    hari_tersedia_siang = VALUES(hari_tersedia_siang),
                    no_wa = VALUES(no_wa)
                """,
                (
                    t["kode_guru"],
                    t["nama_guru"],
                    t["hari_tersedia"],
                    t["shift_pagi"],
                    t["shift_siang"],
                    t["hari_tersedia_pagi"],
                    t["hari_tersedia_siang"],
                    t["no_wa"],
                ),
            )
            if cur.rowcount:
                guru_count += 1
        logger.info(f"  → {guru_count} guru baru dimasukkan/diperbarui (dari {len(teachers_list)} total).")

        # ── 5. Bangun lookup kode_guru → id_guru ──────────────────────
        cur.execute("SELECT id_guru, kode_guru FROM teachers")
        guru_map: dict[int, int] = {row["kode_guru"]: row["id_guru"] for row in cur.fetchall()}

        # ── 6. Insert relasi teacher_subjects ─────────────────────────
        logger.info("Memasukkan relasi guru ↔ mata pelajaran...")
        rel_count  = 0
        err_count  = 0
        for kode_guru, mapel_list in teacher_subjects_dict.items():
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
                    INSERT IGNORE INTO teacher_subjects (id_guru, id_mapel)
                    VALUES (%s, %s)
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
        if branch == "jakarta":
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("TRUNCATE TABLE class_subjects;")
            cur.execute("TRUNCATE TABLE classes;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()

            for name, shift, lvl, major in CLASSES_JAKARTA:
                cur.execute(
                    """
                    INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        shift_operasional = VALUES(shift_operasional),
                        tingkat = VALUES(tingkat),
                        jurusan = VALUES(jurusan)
                    """,
                    (name, shift, lvl, major)
                )
            conn.commit()

            # Build lookup maps for Jakarta
            cur.execute("SELECT id_kelas, nama_kelas FROM classes")
            class_map = {row["nama_kelas"]: row["id_kelas"] for row in cur.fetchall()}
            cur.execute("SELECT id_mapel, nama_mapel FROM subjects")
            subject_map = {row["nama_mapel"]: row["id_mapel"] for row in cur.fetchall()}
            
            logger.info("  -> Menghubungkan alokasi JP untuk kelas Jakarta...")
            alloc_count = 0
            for name, _, _, _ in CLASSES_JAKARTA:
                parts = name.split()
                lvl = parts[0]
                major = parts[1]
                if lvl == "XII" and major == "AK":
                    major = "AKL"
                curr_key = f"{lvl} {major}"
                
                curr_alloc = CURRICULA_JAKARTA.get(curr_key)
                if not curr_alloc:
                    logger.warning(f"  ⚠ Kurikulum untuk key '{curr_key}' tidak ditemukan!")
                    continue
                    
                id_kelas = class_map.get(name)
                if id_kelas is None:
                    continue
                    
                for mapel_name, durasi in curr_alloc.items():
                    id_mapel = subject_map.get(mapel_name)
                    if id_mapel is None:
                        logger.error(f"  ✗ Mapel '{mapel_name}' di kurikulum '{curr_key}' tidak ada di DB!")
                        continue
                    cur.execute(
                        """
                        INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE durasi_jp = VALUES(durasi_jp)
                        """,
                        (id_kelas, id_mapel, durasi)
                    )
                    alloc_count += 1
            conn.commit()
            logger.info(f"  -> Data kelas Jakarta berhasil di-seed (25 kelas) dengan {alloc_count} alokasi JP.")
        else:
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
                    ON DUPLICATE KEY UPDATE
                        shift_operasional = VALUES(shift_operasional),
                        tingkat = VALUES(tingkat),
                        jurusan = VALUES(jurusan)
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
                    ON DUPLICATE KEY UPDATE durasi_jp = VALUES(durasi_jp)
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
