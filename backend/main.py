"""
main.py - FastAPI application entry point
SITAB: Automatic Timetable Generator (Dual-Shift SMK)
Database: Supabase (PostgreSQL via psycopg2)
Schema: class_subjects tanpa id_guru; timetable via id_class_subject
"""
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import io
import json
import logging
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymysql
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openpyxl import Workbook

from backend.database import (
    init_db, get_db_connection, db_fetchall, db_fetchone,
    get_setting, save_setting, clear_master_data, active_branch,
)
from backend.models import (
    Teacher, TeacherCreate,
    Class,   ClassCreate,
    Subject, SubjectCreate,
    ClassSubject, ClassSubjectCreate,
    TeacherSubject, TeacherSubjectCreate,
    SettingsUpdate, AllocationUpdate, AllocationCopy,
)
from backend.solver import generate_timetable, _diagnose_infeasibility, _preflight
from backend.sheets import (
    pull_master_data, export_timetable_to_sheet, pull_excel_data,
    import_teachers_from_excel, import_subjects_from_excel, import_teacher_subjects_from_excel,
)
from backend.excel_generator import generate_excel_timetable


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

init_db()

app = FastAPI(title="SITAB - Automatic Timetable Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.middleware("http")
async def db_schema_middleware(request, call_next):
    # Dapatkan cabang dari query params atau header X-Branch
    branch = request.query_params.get("branch", "").strip().lower()
    if not branch:
        branch = request.headers.get("X-Branch", "bekasi").strip().lower()
    if branch not in ["bekasi", "jakarta"]:
        branch = "bekasi"
        
    token = active_branch.set(branch)
    try:
        response = await call_next(request)
        return response
    finally:
        active_branch.reset(token)

DAYS_ORDER   = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
SHIFT_LIMITS = {
    "PAGI":  {"SENIN": 7, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 7},
    "SIANG": {"SENIN": 7, "SELASA": 7, "RABU": 7, "KAMIS": 7, "JUMAT": 6, "SABTU": 6},
}


# ═══════════════════════════════════════════════
#  Settings
# ═══════════════════════════════════════════════

@app.get("/api/settings")
def get_system_settings():
    return {
        "spreadsheet_id":   get_setting("spreadsheet_id", ""),
        "credentials_json": get_setting("credentials_json", ""),
        "lms_api_url":      get_setting("lms_api_url", ""),
        "lms_api_key":      get_setting("lms_api_key", ""),
    }

@app.post("/api/settings")
def update_system_settings(body: SettingsUpdate):
    if body.credentials_json:
        try:
            json.loads(body.credentials_json)
        except json.JSONDecodeError:
            raise HTTPException(400, "Format Credentials JSON tidak valid!")
    save_setting("spreadsheet_id",   body.spreadsheet_id)
    save_setting("credentials_json", body.credentials_json)
    save_setting("lms_api_url",      body.lms_api_url or "")
    save_setting("lms_api_key",      body.lms_api_key or "")
    return {"status": "SUCCESS", "message": "Pengaturan berhasil disimpan!"}


# ═══════════════════════════════════════════════
#  Clear all data
# ═══════════════════════════════════════════════

@app.post("/api/clear")
def clear_all_data():
    try:
        clear_master_data()
        return {"status": "SUCCESS", "message": "Semua data master & jadwal berhasil dihapus!"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════
#  Template Excel (5 sheets)
# ═══════════════════════════════════════════════

@app.get("/api/template")
def download_template():
    wb = Workbook()

    ws1 = wb.active
    ws1.title = "master_guru"
    ws1.append(["nama_guru", "kode_guru", "hari_tersedia", "shift_pagi", "shift_siang",
                 "hari_tersedia_pagi", "hari_tersedia_siang", "min_jp", "max_jp", "no_wa"])
    ws1.append(["Budi Santoso, S.Pd",  101, "SENIN,SELASA,RABU,KAMIS",               "YA", "TIDAK", "SENIN,SELASA,RABU,KAMIS", "", "", "", "081234567890"])
    ws1.append(["Siti Aminah, S.Pd",   102, "SENIN,RABU,KAMIS,JUMAT,SABTU",           "YA", "YA",    "SENIN,RABU,KAMIS", "JUMAT,SABTU", "", "", "089876543210"])
    ws1.append(["Eko Prasetyo, S.Kom", 103, "SENIN,SELASA,RABU,KAMIS,JUMAT,SABTU",   "YA", "YA",    "SENIN,SELASA,RABU,KAMIS,JUMAT,SABTU", "SENIN,SELASA,RABU,KAMIS,JUMAT,SABTU", "", "", "085544332211"])

    ws2 = wb.create_sheet("master_kelas")
    ws2.append(["nama_kelas", "shift_operasional", "tingkat", "jurusan"])
    ws2.append(["X TKJ 1",  "PAGI",  "X",  "TKJ"])
    ws2.append(["XI AKL 1", "SIANG", "XI", "AKL"])

    ws3 = wb.create_sheet("master_mapel")
    ws3.append(["nama_mapel", "kategori_mapel", "tingkat", "jurusan"])
    ws3.append(["Matematika",     "UMUM",      "", ""])
    ws3.append(["Penjasorkes",    "OLAHRAGA",  "", ""])
    ws3.append(["Pemrograman Web","PRODUKTIF", "X","TKJ"])

    ws4 = wb.create_sheet("alokasi_kurikulum")
    ws4.append(["nama_kelas", "nama_mapel", "durasi_jp"])
    ws4.append(["X TKJ 1", "Matematika",     4])
    ws4.append(["X TKJ 1", "Penjasorkes",    2])
    ws4.append(["X TKJ 1", "Pemrograman Web",30])

    ws5 = wb.create_sheet("penugasan_guru")
    ws5.append(["nama_guru", "nama_mapel"])
    ws5.append(["Budi Santoso, S.Pd",  "Matematika"])
    ws5.append(["Siti Aminah, S.Pd",   "Penjasorkes"])
    ws5.append(["Eko Prasetyo, S.Kom", "Pemrograman Web"])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="template_sitab.xlsx"'},
    )


# ═══════════════════════════════════════════════
#  Google Sheets sync & Excel Upload
# ═══════════════════════════════════════════════

@app.post("/api/upload")
async def upload_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return pull_excel_data(contents)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/teachers/upload")
async def upload_teachers_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return import_teachers_from_excel(contents)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/subjects/upload")
async def upload_subjects_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return import_subjects_from_excel(contents)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/teacher-subjects/upload")
async def upload_teacher_subjects_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return import_teacher_subjects_from_excel(contents)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/sync/pull")
def sync_pull():
    try:
        return pull_master_data()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/sync/push")
def sync_push():
    try:
        return export_timetable_to_sheet()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/sync/lms")
def sync_to_lms():
    import urllib.request
    import urllib.error
    import ssl
    from urllib.parse import urlparse
    
    conn = get_db_connection()
    try:
        lms_url = get_setting("lms_api_url", "").strip()
        lms_key = get_setting("lms_api_key", "").strip()
        
        if not lms_url or not lms_key:
            raise HTTPException(400, "LMS API URL dan API Key belum dikonfigurasi di Pengaturan!")
            
        # Normalisasi URL agar selalu mengarah ke endpoint API /api/v1/sync-all
        # Mengatasi kasus jika user menginput domain utama atau URL halaman admin login
        parsed_url = urlparse(lms_url)
        scheme = parsed_url.scheme or "https"
        netloc = parsed_url.netloc
        if not netloc and parsed_url.path:
            parts = parsed_url.path.split('/')
            netloc = parts[0]
        lms_url = f"{scheme}://{netloc}/api/v1/sync-all"
            
        teachers = db_fetchall(conn, "SELECT * FROM teachers ORDER BY nama_guru")
        for t in teachers:
            t["hari_tersedia"]       = json.loads(t["hari_tersedia"] or "[]")
            t["shift_pagi"]          = bool(t["shift_pagi"])
            t["shift_siang"]         = bool(t["shift_siang"])
            t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"])  if t.get("hari_tersedia_pagi")  else None
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"]) if t.get("hari_tersedia_siang") else None
            t["min_jp"]              = t.get("min_jp")
            t["max_jp"]              = t.get("max_jp")
            t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"])     if t.get("allowed_jp_pagi")     else None
            t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"])    if t.get("allowed_jp_siang")    else None
            
        classes = db_fetchall(conn, "SELECT nama_kelas, shift_operasional, tingkat, jurusan FROM classes ORDER BY nama_kelas")
        subjects = db_fetchall(conn, "SELECT nama_mapel, kategori_mapel, tingkat, jurusan FROM subjects ORDER BY nama_mapel")
        
        teacher_subjects = db_fetchall(conn, """
            SELECT t.kode_guru, s.nama_mapel
            FROM teacher_subjects ts
            JOIN teachers t ON ts.id_guru = t.id_guru
            JOIN subjects s ON ts.id_mapel = s.id_mapel
            ORDER BY t.nama_guru, s.nama_mapel
        """)
        
        class_subjects = db_fetchall(conn, """
            SELECT c.nama_kelas, s.nama_mapel, cs.durasi_jp, t.kode_guru AS kode_guru_mutlak
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            LEFT JOIN teachers t ON cs.id_guru_mutlak = t.id_guru
            ORDER BY c.nama_kelas, s.nama_mapel
        """)
        
        timetable = db_fetchall(conn, """
            SELECT c.nama_kelas, s.nama_mapel, g.kode_guru, t.hari, t.jam_ke,
                   t.is_fallback, gorig.kode_guru AS original_guru_kode
            FROM timetable t
            JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            LEFT JOIN teachers g ON t.id_guru = g.id_guru
            LEFT JOIN teachers gorig ON t.original_guru_id = gorig.id_guru
            ORDER BY c.nama_kelas, t.hari, t.jam_ke
        """)
        for slot in timetable:
            slot["is_fallback"] = bool(slot["is_fallback"])
            
        payload = {
            "teachers": teachers,
            "classes": classes,
            "subjects": subjects,
            "teacher_subjects": teacher_subjects,
            "class_subjects": class_subjects,
            "timetable": timetable
        }
        
        import datetime
        def default_serializer(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(
                lms_url,
                data=json.dumps(payload, default=default_serializer).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {lms_key}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                return {"status": "SUCCESS", "message": res_json.get("message", "Sinkronisasi ke LMS berhasil!")}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            logger.error(f"HTTPError syncing to LMS: {err_body}")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("message", str(e))
            except Exception:
                msg = err_body[:200] or str(e)
            raise HTTPException(status_code=e.code, detail=f"LMS Server Error: {msg}")
        except Exception as e:
            logger.exception("Connection error to LMS")
            raise HTTPException(status_code=500, detail=f"Gagal menghubungi server LMS: {e}")
            
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  Solver
# ═══════════════════════════════════════════════

@app.post("/api/generate")
def run_generator():
    try:
        return generate_timetable()
    except Exception as e:
        logger.exception("Generator error")
        raise HTTPException(500, f"Gagal generate jadwal: {e}")

@app.post("/api/generate/abort")
def abort_generation():
    from backend.solver import interrupt_active_solver
    success = interrupt_active_solver()
    return {"status": "SUCCESS" if success else "FAILED"}

@app.get("/api/generate/status")
def get_generation_status():
    from backend.solver import active_stage, active_solver
    return {
        "is_running": active_solver is not None or active_stage > 0,
        "stage": active_stage
    }



# ═══════════════════════════════════════════════
#  Coverage Warning (Blueprint para 2 Warning System)
# ═══════════════════════════════════════════════

@app.get("/api/coverage")
def get_coverage_warnings():
    conn = get_db_connection()
    try:
        classes  = db_fetchall(conn, "SELECT * FROM classes")
        teachers = db_fetchall(conn, "SELECT * FROM teachers")

        for t in teachers:
            t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"]  or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            t["shift_pagi"]  = bool(t["shift_pagi"])
            t["shift_siang"] = bool(t["shift_siang"])

        warnings = []
        summary  = []

        for shift in ["PAGI", "SIANG"]:
            n_kelas = sum(1 for c in classes if c["shift_operasional"] == shift)
            if n_kelas == 0:
                continue
            for day in DAYS_ORDER:
                if shift == "PAGI":
                    n_guru = sum(1 for t in teachers if t["shift_pagi"] and day in t["hari_tersedia_pagi"])
                else:
                    n_guru = sum(1 for t in teachers if t["shift_siang"] and day in t["hari_tersedia_siang"])

                entry = {
                    "shift": shift, "hari": day,
                    "kelas_aktif": n_kelas, "guru_tersedia": n_guru,
                    "cukup": n_guru >= n_kelas,
                    "kekurangan": max(0, n_kelas - n_guru),
                }
                summary.append(entry)
                if n_guru < n_kelas:
                    warnings.append(
                        f"Shift {shift}, {day}: {n_kelas} kelas aktif, "
                        f"{n_guru} guru tersedia (kekurangan {n_kelas - n_guru})"
                    )

        return {
            "status":   "OK" if not warnings else "WARNING",
            "warnings": warnings,
            "summary":  summary,
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  Validasi Pre-Flight
# ═══════════════════════════════════════════════

@app.post("/api/validate")
def validate_data():
    conn = get_db_connection()
    try:
        errors   = []
        warnings = []

        classes  = db_fetchall(conn, "SELECT * FROM classes ORDER BY nama_kelas")
        teachers = db_fetchall(conn, "SELECT * FROM teachers ORDER BY nama_guru")

        for t in teachers:
            t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"]  or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            t["shift_pagi"]  = bool(t["shift_pagi"])
            t["shift_siang"] = bool(t["shift_siang"])
            t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"])     if t.get("allowed_jp_pagi")     else None
            t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"])    if t.get("allowed_jp_siang")    else None

        allocations = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp,
                   c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
            FROM   class_subjects cs
            JOIN   classes  c ON cs.id_kelas = c.id_kelas
            JOIN   subjects s ON cs.id_mapel  = s.id_mapel
            ORDER BY c.nama_kelas, s.nama_mapel
        """)

        ts_rows = db_fetchall(conn, "SELECT id_guru, id_mapel FROM teacher_subjects")
        ts_set  = {(r["id_guru"], r["id_mapel"]) for r in ts_rows}

        if not classes:
            errors.append("Belum ada data kelas.")
        if not allocations:
            errors.append("Belum ada alokasi kurikulum.")
        if not ts_rows:
            errors.append("Belum ada penugasan guru (teacher_subjects kosong). Isi Tab 5 dulu.")

        subjects = db_fetchall(conn, "SELECT * FROM subjects")
        subjects_map = {s["id_mapel"]: s for s in subjects}

        if not errors:
            # Panggil preflight terpadu
            pre_errs, pre_warns = _preflight(teachers, classes, allocations, ts_set, subjects_map)
            errors.extend(pre_errs)
            warnings.extend(pre_warns)

            # Tambahkan juga peringatan kekurangan coverage harian biasa (bukan blocker keras)
            for shift in ["PAGI", "SIANG"]:
                n_kelas = sum(1 for c in classes if c["shift_operasional"] == shift)
                if n_kelas == 0:
                    continue
                for day in DAYS_ORDER:
                    if shift == "PAGI":
                        n_guru = sum(1 for t in teachers if t["shift_pagi"] and day in t["hari_tersedia_pagi"])
                    else:
                        n_guru = sum(1 for t in teachers if t["shift_siang"] and day in t["hari_tersedia_siang"])
                    if n_guru < n_kelas:
                        warnings.append(
                            f"Coverage - Shift {shift}, {day}: "
                            f"{n_kelas} kelas aktif, {n_guru} guru tersedia "
                            f"(kekurangan {n_kelas - n_guru})."
                        )

        no_qual = sum(1 for a in allocations if not any(mid == a["id_mapel"] for (_, mid) in ts_set))
        summary_lines = [
            f"Total kelas        : {len(classes)}",
            f"Total alokasi      : {len(allocations)} entri",
            f"Relasi guru-mapel  : {len(ts_rows)}",
            f"Alokasi tanpa guru : {no_qual}",
            f"Error ditemukan    : {len(errors)}",
            f"Peringatan         : {len(warnings)}",
        ]

        return {
            "status":   "OK" if not errors else "ERROR",
            "errors":   errors,
            "warnings": warnings,
            "summary":  summary_lines,
            "stats": {
                "total_classes":     len(classes),
                "total_allocations": len(allocations),
                "ts_count":          len(ts_rows),
                "no_qual_count":     no_qual,
                "error_count":       len(errors),
                "warning_count":     len(warnings),
            },
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  Health Check Dashboard
# ═══════════════════════════════════════════════

@app.get("/api/health")
def get_health():
    """
    Mengembalikan anomali terstruktur per kategori untuk ditampilkan di dashboard.
    Semua isu yang bisa mencegah generate jadwal dikelompokkan berdasarkan tipe.
    """
    conn = get_db_connection()
    try:
        classes  = db_fetchall(conn, "SELECT * FROM classes ORDER BY nama_kelas")
        teachers = db_fetchall(conn, "SELECT * FROM teachers ORDER BY nama_guru")
        subjects = db_fetchall(conn, "SELECT * FROM subjects ORDER BY nama_mapel")

        for t in teachers:
            t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"]  or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            t["shift_pagi"]  = bool(t["shift_pagi"])
            t["shift_siang"] = bool(t["shift_siang"])
            t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"])     if t.get("allowed_jp_pagi")     else None
            t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"])    if t.get("allowed_jp_siang")    else None

        allocations = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp,
                   c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
            FROM   class_subjects cs
            JOIN   classes  c ON cs.id_kelas = c.id_kelas
            JOIN   subjects s ON cs.id_mapel  = s.id_mapel
            ORDER BY c.nama_kelas, s.nama_mapel
        """)

        ts_rows = db_fetchall(conn, "SELECT id_guru, id_mapel FROM teacher_subjects")
        ts_set  = {(r["id_guru"], r["id_mapel"]) for r in ts_rows}
        teachers_map = {t["id_guru"]: t for t in teachers}
        subjects_map = {s["id_mapel"]: s for s in subjects}

        issues = {
            "jp_lebih":            [],  # JP > 40 (ERROR - blocker)
            "jp_kurang":           [],  # JP < 40 (WARNING)
            "mapel_tanpa_guru":    [],  # Alokasi kelas tanpa guru layak (ERROR - blocker)
            "mapel_no_assignment": [],  # Mapel aktif tanpa guru sama sekali (ERROR - blocker)
            "guru_tanpa_mapel":    [],  # Guru belum punya penugasan (WARNING)
            "guru_idle_expert":    [],  # Guru punya keahlian mapel aktif tapi shift tidak match (WARNING)
            "kelas_tanpa_alokasi": [],  # Kelas belum punya alokasi JP (WARNING)
            "olahraga_jp_salah":   [],  # Olahraga harus tepat 2 JP (ERROR - blocker)
            "coverage_kritis":     [],  # Hari dengan kekurangan guru parah (WARNING)
            "feasibility_errors":  [],  # Bottleneck guru / kelayakan (ERROR - blocker)
        }

        # ── 1. JP per kelas ──────────────────────────────────────────
        class_jp: dict = {}
        class_alloc_count: dict = {}
        class_mapel_list: dict = {}
        for a in allocations:
            class_jp[a["id_kelas"]]          = class_jp.get(a["id_kelas"], 0) + a["durasi_jp"]
            class_alloc_count[a["id_kelas"]] = class_alloc_count.get(a["id_kelas"], 0) + 1
            class_mapel_list.setdefault(a["id_kelas"], []).append(a["nama_mapel"])

        for c in classes:
            total   = class_jp.get(c["id_kelas"], 0)
            alloc_n = class_alloc_count.get(c["id_kelas"], 0)
            mapels  = class_mapel_list.get(c["id_kelas"], [])
            if alloc_n == 0:
                issues["kelas_tanpa_alokasi"].append({
                    "kelas": c["nama_kelas"],
                    "shift": c["shift_operasional"],
                    "tingkat": c["tingkat"],
                    "jurusan": c["jurusan"],
                })
            elif total > 40:
                issues["jp_lebih"].append({
                    "kelas":    c["nama_kelas"],
                    "shift":    c["shift_operasional"],
                    "total_jp": total,
                    "selisih":  total - 40,
                    "mapels":   mapels,
                })
            elif total < 40:
                issues["jp_kurang"].append({
                    "kelas":    c["nama_kelas"],
                    "shift":    c["shift_operasional"],
                    "total_jp": total,
                    "selisih":  40 - total,
                    "jumlah_mapel": alloc_n,
                })

        # ── 2. Olahraga JP ──────────────────────────────────────────
        for a in allocations:
            k   = (a.get("nama_mapel") or "").upper()
            kat = (a.get("kategori_mapel") or "").upper()
            is_olah = any(kw in k for kw in ("JASMANI","OLAH RAGA","PENJASORKES","OLAHRAGA","PJOK")) or "OLAHRAGA" in kat
            if is_olah and a["durasi_jp"] != 2:
                issues["olahraga_jp_salah"].append({
                    "kelas":      a["nama_kelas"],
                    "shift":      a["shift_operasional"],
                    "nama_mapel": a["nama_mapel"],
                    "jp_saat_ini": a["durasi_jp"],
                    "hint": "Aturan blok 2 JP berturut-turut wajib dipenuhi solver",
                })

        # ── 3. Alokasi tanpa guru layak ─────────────────────────────
        for a in allocations:
            shift = a["shift_operasional"]
            # Guru yang kualifikasi PERSIS mapel ini
            qualified_ids = [
                gid for (gid, mid) in ts_set
                if mid == a["id_mapel"]
                and teachers_map.get(gid)
                and ((shift == "PAGI"  and teachers_map[gid]["shift_pagi"]) or
                     (shift == "SIANG" and teachers_map[gid]["shift_siang"]))
            ]
            # Guru yang punya keahlian mapel ini tapi shift tidak cocok
            wrong_shift_ids = [
                gid for (gid, mid) in ts_set
                if mid == a["id_mapel"]
                and teachers_map.get(gid)
                and not ((shift == "PAGI"  and teachers_map[gid]["shift_pagi"]) or
                         (shift == "SIANG" and teachers_map[gid]["shift_siang"]))
            ]
            wrong_shift_names = [teachers_map[gid]["nama_guru"] for gid in wrong_shift_ids if gid in teachers_map]

            # Cek kategori mapel untuk saran fallback
            any_assigned = any(mid == a["id_mapel"] for (_, mid) in ts_set)
            if not qualified_ids:
                issues["mapel_tanpa_guru"].append({
                    "kelas":          a["nama_kelas"],
                    "shift":          a["shift_operasional"],
                    "nama_mapel":     a["nama_mapel"],
                    "kategori":       a["kategori_mapel"],
                    "durasi_jp":      a["durasi_jp"],
                    "ada_guru_lain_shift": any_assigned,
                    "guru_shift_salah":    wrong_shift_names,
                })

        # ── 4. Mapel di master tanpa guru sama sekali ───────────────
        assigned_mapel_ids = {mid for (_, mid) in ts_set}
        used_mapel_ids     = {a["id_mapel"] for a in allocations}
        # Hitung berapa kelas pakai mapel ini
        mapel_kelas_count: dict = {}
        for a in allocations:
            mapel_kelas_count[a["id_mapel"]] = mapel_kelas_count.get(a["id_mapel"], 0) + 1

        for s in subjects:
            if s["id_mapel"] in used_mapel_ids and s["id_mapel"] not in assigned_mapel_ids:
                issues["mapel_no_assignment"].append({
                    "id_mapel":    s["id_mapel"],
                    "nama_mapel":  s["nama_mapel"],
                    "kategori":    s["kategori_mapel"],
                    "dipakai_kelas": mapel_kelas_count.get(s["id_mapel"], 0),
                })

        # ── 5. Guru tanpa penugasan mapel apapun ────────────────────
        assigned_guru_ids = {gid for (gid, _) in ts_set}
        for t in teachers:
            if t["id_guru"] not in assigned_guru_ids:
                shift_label = []
                if t["shift_pagi"]:  shift_label.append("PAGI")
                if t["shift_siang"]: shift_label.append("SIANG")
                issues["guru_tanpa_mapel"].append({
                    "nama_guru": t["nama_guru"],
                    "kode_guru": t["kode_guru"],
                    "shift":     "/".join(shift_label) if shift_label else "-",
                    "hint":      "Guru tidak akan pernah dijadwalkan oleh solver",
                })

        # ── 6. Guru idle expert: punya keahlian mapel aktif, tapi shift tidak ada kelas ─────
        classes_pagi  = [c for c in classes if c["shift_operasional"] == "PAGI"]
        classes_siang = [c for c in classes if c["shift_operasional"] == "SIANG"]
        for t in teachers:
            if t["id_guru"] not in assigned_guru_ids:
                continue  # sudah masuk guru_tanpa_mapel
            # Cari keahlian mapel yang aktif dipakai di alokasi
            expert_mapels = [
                subjects_map[mid]["nama_mapel"]
                for (gid, mid) in ts_set
                if gid == t["id_guru"] and mid in used_mapel_ids and mid in subjects_map
            ]
            if not expert_mapels:
                continue
            hints = []
            # Guru shift pagi tapi tidak ada kelas pagi
            if t["shift_pagi"] and not classes_pagi:
                hints.append("Guru shift PAGI tapi tidak ada kelas shift PAGI")
            # Guru shift siang tapi tidak ada kelas siang
            if t["shift_siang"] and not classes_siang:
                hints.append("Guru shift SIANG tapi tidak ada kelas shift SIANG")
            # Guru punya keahlian mapel aktif di shift yang ada kelas, tapi hari tersedia 0
            if t["shift_pagi"] and classes_pagi and not t["hari_tersedia_pagi"]:
                hints.append("Guru shift PAGI tidak punya hari tersedia pagi sama sekali")
            if t["shift_siang"] and classes_siang and not t["hari_tersedia_siang"]:
                hints.append("Guru shift SIANG tidak punya hari tersedia siang sama sekali")
            if hints:
                issues["guru_idle_expert"].append({
                    "nama_guru":    t["nama_guru"],
                    "kode_guru":    t["kode_guru"],
                    "shift":        "/".join([
                        ("PAGI" if t["shift_pagi"] else ""),
                        ("SIANG" if t["shift_siang"] else "")
                    ]).strip("/"),
                    "keahlian_mapel": expert_mapels,
                    "hints":        hints,
                })

        # ── 7. Coverage kritis per shift × hari ─────────────────────
        for shift in ["PAGI", "SIANG"]:
            n_kelas = sum(1 for c in classes if c["shift_operasional"] == shift)
            if n_kelas == 0:
                continue
            for day in DAYS_ORDER:
                if shift == "PAGI":
                    n_guru = sum(1 for t in teachers if t["shift_pagi"] and day in t["hari_tersedia_pagi"])
                else:
                    n_guru = sum(1 for t in teachers if t["shift_siang"] and day in t["hari_tersedia_siang"])

                kekurangan = max(0, n_kelas - n_guru)
                pct_kurang = round(kekurangan / n_kelas * 100) if n_kelas else 0

                if kekurangan > 0:
                    # Siapa saja guru yang tersedia di hari ini?
                    guru_tersedia_names = [
                        t["nama_guru"] for t in teachers
                        if (shift == "PAGI" and t["shift_pagi"] and day in t["hari_tersedia_pagi"]) or
                           (shift == "SIANG" and t["shift_siang"] and day in t["hari_tersedia_siang"])
                    ]
                    severity = "KRITIS" if pct_kurang >= 50 else "KURANG"
                    issues["coverage_kritis"].append({
                        "shift":         shift,
                        "hari":          day,
                        "kelas_aktif":   n_kelas,
                        "guru_tersedia": n_guru,
                        "kekurangan":    kekurangan,
                        "pct_kurang":    pct_kurang,
                        "severity":      severity,
                        "guru_hadir":    guru_tersedia_names,
                    })

        # ── 8. Feasibility Errors (deep analysis) ────────────────────
        issues["feasibility_errors"] = _diagnose_infeasibility(teachers, classes, allocations, ts_set, subjects_map)

        # ── Hitung total error blocker ───────────────────────────────
        total_errors   = (len(issues["jp_lebih"]) + len(issues["mapel_tanpa_guru"]) +
                          len(issues["olahraga_jp_salah"]) + len(issues["mapel_no_assignment"]) +
                          len(issues["feasibility_errors"]))
        total_warnings = (len(issues["jp_kurang"]) + len(issues["guru_tanpa_mapel"]) +
                          len(issues["guru_idle_expert"]) + len(issues["kelas_tanpa_alokasi"]) +
                          len(issues["coverage_kritis"]))

        can_generate = (total_errors == 0 and len(classes) > 0
                        and len(allocations) > 0 and len(ts_rows) > 0)

        return {
            "status":          "OK" if can_generate else ("ERROR" if total_errors > 0 else "WARNING"),
            "can_generate":    can_generate,
            "total_errors":    total_errors,
            "total_warnings":  total_warnings,
            "issues":          issues,
            "summary": {
                "total_kelas":     len(classes),
                "total_guru":      len(teachers),
                "total_mapel":     len(subjects),
                "total_alokasi":   len(allocations),
                "total_penugasan": len(ts_rows),
            },
        }
    finally:
        conn.close()


@app.get("/api/feasibility")
def get_feasibility():
    """
    Menghitung kelayakan ketersediaan guru harian (Daily Coverage)
    dan kelayakan beban mata pelajaran (Subject Capacity).
    """
    conn = get_db_connection()
    try:
        classes = db_fetchall(conn, "SELECT id_kelas, nama_kelas, shift_operasional FROM classes")
        teachers = db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp FROM teachers")
        subjects = db_fetchall(conn, "SELECT id_mapel, nama_mapel, kategori_mapel FROM subjects")
        allocations = db_fetchall(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp,
                   c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
            FROM   class_subjects cs
            JOIN   classes  c ON cs.id_kelas = c.id_kelas
            JOIN   subjects s ON cs.id_mapel  = s.id_mapel
        """)
        ts_rows = db_fetchall(conn, "SELECT id_guru, id_mapel FROM teacher_subjects")
        
        # Parse json fields
        for t in teachers:
            t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"]  or "[]")
            t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
            t["shift_pagi"]  = bool(t["shift_pagi"])
            t["shift_siang"] = bool(t["shift_siang"])
            t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"])     if t.get("allowed_jp_pagi")     else None
            t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"])    if t.get("allowed_jp_siang")    else None
            
        teachers_map = {t["id_guru"]: t for t in teachers}
        
        # 1. Daily Coverage Map
        daily_coverage = []
        for shift in ["PAGI", "SIANG"]:
            n_kelas = sum(1 for c in classes if c["shift_operasional"] == shift)
            for day in DAYS_ORDER:
                # Guru yang bersedia hadir di shift & hari ini
                guru_hadir = []
                # Guru yang libur (punya shift ini tapi hari ini off)
                guru_libur = []
                
                for t in teachers:
                    if shift == "PAGI" and t["shift_pagi"]:
                        if day in t["hari_tersedia_pagi"]:
                            guru_hadir.append({"id_guru": t["id_guru"], "nama_guru": t["nama_guru"], "kode_guru": t["kode_guru"]})
                        else:
                            guru_libur.append({"id_guru": t["id_guru"], "nama_guru": t["nama_guru"], "kode_guru": t["kode_guru"]})
                    elif shift == "SIANG" and t["shift_siang"]:
                        if day in t["hari_tersedia_siang"]:
                            guru_hadir.append({"id_guru": t["id_guru"], "nama_guru": t["nama_guru"], "kode_guru": t["kode_guru"]})
                        else:
                            guru_libur.append({"id_guru": t["id_guru"], "nama_guru": t["nama_guru"], "kode_guru": t["kode_guru"]})
                
                n_guru = len(guru_hadir)
                kekurangan = max(0, n_kelas - n_guru)
                
                if n_guru < n_kelas:
                    status = "RED"
                elif n_guru <= n_kelas + 2:
                    status = "YELLOW"
                else:
                    status = "GREEN"
                    
                daily_coverage.append({
                    "shift": shift,
                    "hari": day,
                    "butuh": n_kelas,
                    "tersedia": n_guru,
                    "kekurangan": kekurangan,
                    "status": status,
                    "guru_hadir": guru_hadir,
                    "guru_libur": guru_libur
                })

        # 2. Subject Capacity Map
        subject_capacities = []
        # Group allocations by subject
        subject_demand = {} # mapel_id -> total_jp_required
        subject_classes = {} # mapel_id -> list of class names
        for a in allocations:
            mid = a["id_mapel"]
            subject_demand[mid] = subject_demand.get(mid, 0) + a["durasi_jp"]
            subject_classes.setdefault(mid, []).append(a["nama_kelas"])
            
        # Group teachers by subject qualifications
        subject_teachers = {} # mapel_id -> list of teachers qualified
        for ts in ts_rows:
            mid = ts["id_mapel"]
            gid = ts["id_guru"]
            if gid in teachers_map:
                subject_teachers.setdefault(mid, []).append(teachers_map[gid])
                
        for s in subjects:
            mid = s["id_mapel"]
            demand = subject_demand.get(mid, 0)
            if demand == 0:
                continue # Skip mapel yang tidak dipakai di alokasi kurikulum
                
            qualified_teachers = subject_teachers.get(mid, [])
            total_capacity = sum(t["max_jp"] if t["max_jp"] is not None else 60 for t in qualified_teachers)
            
            gurus_info = []
            for t in qualified_teachers:
                gurus_info.append({
                    "id_guru": t["id_guru"],
                    "nama_guru": t["nama_guru"],
                    "kode_guru": t["kode_guru"],
                    "max_jp": t["max_jp"] if t["max_jp"] is not None else 60
                })
                
            if len(qualified_teachers) == 0:
                status = "RED" # No teachers at all
            elif total_capacity < demand:
                status = "RED" # Not enough capacity
            elif demand > 0.85 * total_capacity:
                status = "YELLOW" # Tight capacity (> 85%)
            else:
                status = "GREEN" # Safe
                
            subject_capacities.append({
                "id_mapel": mid,
                "nama_mapel": s["nama_mapel"],
                "kategori_mapel": s["kategori_mapel"],
                "total_jp_butuh": demand,
                "n_guru": len(qualified_teachers),
                "total_jp_kapasitas": total_capacity,
                "status": status,
                "guru_pengampu": gurus_info,
                "kelas_pemakai": list(set(subject_classes.get(mid, [])))
            })
            
        return {
            "daily_coverage": daily_coverage,
            "subject_capacities": subject_capacities
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  Timetable read (JOIN via id_class_subject)
# ═══════════════════════════════════════════════

@app.get("/api/timetable")
def get_timetable():
    conn = get_db_connection()
    try:
        classes = db_fetchall(conn, "SELECT * FROM classes ORDER BY nama_kelas")
        entries = db_fetchall(conn, """
            SELECT t.id_timetable, t.hari, t.jam_ke,
                   t.is_fallback, t.original_guru_id, t.id_class_subject,
                   cs.id_kelas, cs.id_mapel, cs.durasi_jp,
                   c.nama_kelas, c.shift_operasional,
                   s.nama_mapel, s.kategori_mapel,
                   g.id_guru, g.nama_guru, g.kode_guru
            FROM timetable t
            JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
            JOIN classes  c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel  = s.id_mapel
            LEFT JOIN teachers g ON t.id_guru = g.id_guru
            ORDER BY c.nama_kelas, t.hari, t.jam_ke
        """)

        for e in entries:
            e["is_fallback"] = 1 if e.get("is_fallback") else 0

        total_possible = sum(
            SHIFT_LIMITS[c["shift_operasional"]][d]
            for c in classes
            for d in SHIFT_LIMITS[c["shift_operasional"]]
        )
        fill_pct = round(len(entries) / total_possible * 100, 1) if total_possible else 0.0

        return {
            "timetable": entries,
            "classes":   classes,
            "stats": {
                "total_slots":          len(entries),
                "total_possible_slots": total_possible,
                "fill_percentage":      fill_pct,
                "classes_count":        len(classes),
            },
        }
    finally:
        conn.close()

@app.delete("/api/timetable")
def delete_timetable():
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cur.execute("TRUNCATE TABLE timetable")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        return {"status": "SUCCESS", "message": "Jadwal berhasil direset (dikosongkan)"}
    finally:
        cur.close(); conn.close()


@app.get("/api/timetable/download")
def download_timetable():
    try:
        buf, filename = generate_excel_timetable()
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception("Failed to generate Excel timetable")
        raise HTTPException(500, f"Gagal generate file Excel: {e}")


# ═══════════════════════════════════════════════
#  CRUD - Teachers
# ═══════════════════════════════════════════════

@app.get("/api/teachers", response_model=List[Teacher])
def get_teachers():
    conn = get_db_connection()
    rows = db_fetchall(conn, "SELECT * FROM teachers ORDER BY nama_guru")
    conn.close()
    for d in rows:
        d["hari_tersedia"]       = json.loads(d["hari_tersedia"] or "[]")
        d["shift_pagi"]          = bool(d["shift_pagi"])
        d["shift_siang"]         = bool(d["shift_siang"])
        d["hari_tersedia_pagi"]  = json.loads(d["hari_tersedia_pagi"])  if d.get("hari_tersedia_pagi")  else None
        d["hari_tersedia_siang"] = json.loads(d["hari_tersedia_siang"]) if d.get("hari_tersedia_siang") else None
        d["min_jp"]              = d.get("min_jp")
        d["max_jp"]              = d.get("max_jp")
        d["allowed_jp_pagi"]     = json.loads(d["allowed_jp_pagi"])     if d.get("allowed_jp_pagi")     else None
        d["allowed_jp_siang"]    = json.loads(d["allowed_jp_siang"])    if d.get("allowed_jp_siang")    else None
    return rows

@app.post("/api/teachers", response_model=Teacher)
def create_teacher(body: TeacherCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO teachers
                (nama_guru, kode_guru, hari_tersedia, shift_pagi, shift_siang,
                 hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp,
                 allowed_jp_pagi, allowed_jp_siang, no_wa)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_guru
        """, (
            body.nama_guru, body.kode_guru,
            json.dumps(body.hari_tersedia),
            body.shift_pagi, body.shift_siang,
            json.dumps(body.hari_tersedia_pagi)  if body.hari_tersedia_pagi  else None,
            json.dumps(body.hari_tersedia_siang) if body.hari_tersedia_siang else None,
            body.min_jp,
            body.max_jp,
            json.dumps(body.allowed_jp_pagi)     if body.allowed_jp_pagi     else None,
            json.dumps(body.allowed_jp_siang)    if body.allowed_jp_siang    else None,
            body.no_wa,
        ))
        conn.commit()
        new_id = cur.fetchone()["id_guru"]
        return {**body.model_dump(), "id_guru": new_id}
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, f"Kode guru {body.kode_guru} sudah terdaftar!")
    finally:
        cur.close(); conn.close()

@app.put("/api/teachers/{id_guru}")
def update_teacher(id_guru: int, body: TeacherCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            UPDATE teachers SET
                nama_guru = %s, kode_guru = %s,
                hari_tersedia = %s, shift_pagi = %s, shift_siang = %s,
                hari_tersedia_pagi = %s, hari_tersedia_siang = %s,
                min_jp = %s, max_jp = %s,
                allowed_jp_pagi = %s, allowed_jp_siang = %s,
                no_wa = %s
            WHERE id_guru = %s RETURNING id_guru
        """, (
            body.nama_guru, body.kode_guru,
            json.dumps(body.hari_tersedia),
            body.shift_pagi, body.shift_siang,
            json.dumps(body.hari_tersedia_pagi)  if body.hari_tersedia_pagi  else None,
            json.dumps(body.hari_tersedia_siang) if body.hari_tersedia_siang else None,
            body.min_jp,
            body.max_jp,
            json.dumps(body.allowed_jp_pagi)     if body.allowed_jp_pagi     else None,
            json.dumps(body.allowed_jp_siang)    if body.allowed_jp_siang    else None,
            body.no_wa,
            id_guru,
        ))
        conn.commit()
        if not cur.fetchone():
            raise HTTPException(404, "Guru tidak ditemukan")
        return {**body.model_dump(), "id_guru": id_guru}
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, f"Kode guru {body.kode_guru} sudah terdaftar!")
    finally:
        cur.close(); conn.close()

@app.delete("/api/teachers/{id_guru}")
def delete_teacher(id_guru: int):
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM teachers WHERE id_guru = %s", (id_guru,))
    conn.commit(); cur.close(); conn.close()
    return {"status": "SUCCESS", "message": "Guru berhasil dihapus"}


# ═══════════════════════════════════════════════
#  CRUD - Classes
# ═══════════════════════════════════════════════

def _auto_tingkat_jurusan(nama_kelas: str):
    parts = nama_kelas.split()
    if len(parts) >= 2:
        tk = parts[0].upper()
        if tk in ("X", "XI", "XII"):
            return tk, parts[1].upper()
    return None, None

@app.get("/api/classes", response_model=List[Class])
def get_classes():
    conn = get_db_connection()
    rows = db_fetchall(conn, "SELECT * FROM classes ORDER BY nama_kelas")
    conn.close()
    return rows

@app.post("/api/classes", response_model=Class)
def create_class(body: ClassCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        nama  = body.nama_kelas.strip()
        shift = body.shift_operasional.upper()
        tk, jr = _auto_tingkat_jurusan(nama)
        tingkat = body.tingkat or tk
        jurusan = body.jurusan or jr
        cur.execute(
            "INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan) VALUES (%s,%s,%s,%s) RETURNING id_kelas",
            (nama, shift, tingkat, jurusan)
        )
        conn.commit()
        new_id = cur.fetchone()["id_kelas"]
        return {**body.model_dump(), "id_kelas": new_id, "tingkat": tingkat, "jurusan": jurusan}
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, "Nama kelas sudah terdaftar!")
    finally:
        cur.close(); conn.close()

@app.patch("/api/classes/{id_kelas}")
def update_class(id_kelas: int, body: ClassCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        nama  = body.nama_kelas.strip()
        shift = body.shift_operasional.upper()
        tk, jr = _auto_tingkat_jurusan(nama)
        tingkat = body.tingkat or tk
        jurusan = body.jurusan or jr
        cur.execute("""
            UPDATE classes SET nama_kelas=%s, shift_operasional=%s, tingkat=%s, jurusan=%s
            WHERE id_kelas=%s RETURNING id_kelas
        """, (nama, shift, tingkat, jurusan, id_kelas))
        conn.commit()
        if not cur.fetchone():
            raise HTTPException(404, "Kelas tidak ditemukan")
        return {**body.model_dump(), "id_kelas": id_kelas, "tingkat": tingkat, "jurusan": jurusan}
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, "Nama kelas sudah terdaftar!")
    finally:
        cur.close(); conn.close()

@app.delete("/api/classes/{id_kelas}")
def delete_class(id_kelas: int):
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM classes WHERE id_kelas = %s", (id_kelas,))
    conn.commit(); cur.close(); conn.close()
    return {"status": "SUCCESS", "message": "Kelas berhasil dihapus"}


# ═══════════════════════════════════════════════
#  CRUD - Subjects
# ═══════════════════════════════════════════════

@app.get("/api/subjects", response_model=List[Subject])
def get_subjects(id_kelas: Optional[int] = None):
    conn = get_db_connection()
    try:
        if id_kelas:
            kelas = db_fetchone(conn, "SELECT tingkat, jurusan FROM classes WHERE id_kelas = %s", (id_kelas,))
            if kelas:
                sql, params = "SELECT * FROM subjects WHERE 1=1", []
                if kelas.get("jurusan"):
                    sql += " AND (jurusan IS NULL OR jurusan = '' OR UPPER(jurusan) = UPPER(%s))"
                    params.append(kelas["jurusan"])
                if kelas.get("tingkat"):
                    sql += " AND (tingkat IS NULL OR tingkat = '' OR UPPER(tingkat) = UPPER(%s))"
                    params.append(kelas["tingkat"])
                sql += " ORDER BY nama_mapel"
                return db_fetchall(conn, sql, tuple(params))
        return db_fetchall(conn, "SELECT * FROM subjects ORDER BY nama_mapel")
    finally:
        conn.close()

@app.post("/api/subjects", response_model=Subject)
def create_subject(body: SubjectCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO subjects (nama_mapel, kategori_mapel, tingkat, jurusan) VALUES (%s,%s,%s,%s) RETURNING id_mapel",
            (body.nama_mapel.strip(), body.kategori_mapel.upper(),
             body.tingkat.strip().upper() if body.tingkat else None,
             body.jurusan.strip().upper() if body.jurusan else None)
        )
        conn.commit()
        new_id = cur.fetchone()["id_mapel"]
        return {**body.model_dump(), "id_mapel": new_id}
    finally:
        cur.close(); conn.close()

@app.patch("/api/subjects/{id_mapel}")
def update_subject(id_mapel: int, body: SubjectCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            UPDATE subjects SET nama_mapel=%s, kategori_mapel=%s, tingkat=%s, jurusan=%s
            WHERE id_mapel=%s RETURNING id_mapel
        """, (
            body.nama_mapel.strip(), body.kategori_mapel.upper(),
            body.tingkat.strip().upper() if body.tingkat else None,
            body.jurusan.strip().upper() if body.jurusan else None,
            id_mapel,
        ))
        conn.commit()
        if not cur.fetchone():
            raise HTTPException(404, "Mata pelajaran tidak ditemukan")
        return {**body.model_dump(), "id_mapel": id_mapel}
    finally:
        cur.close(); conn.close()

@app.delete("/api/subjects/{id_mapel}")
def delete_subject(id_mapel: int):
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE id_mapel = %s", (id_mapel,))
    conn.commit(); cur.close(); conn.close()
    return {"status": "SUCCESS", "message": "Mata Pelajaran berhasil dihapus"}


# ═══════════════════════════════════════════════
#  CRUD - Class Subjects (Alokasi - tanpa id_guru)
# ═══════════════════════════════════════════════

@app.get("/api/allocations", response_model=List[ClassSubject])
def get_allocations():
    conn = get_db_connection()
    rows = db_fetchall(conn, """
        SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
               c.nama_kelas, s.nama_mapel, tg.nama_guru AS nama_guru_mutlak
        FROM   class_subjects cs
        JOIN   classes  c ON cs.id_kelas = c.id_kelas
        JOIN   subjects s ON cs.id_mapel  = s.id_mapel
        LEFT JOIN teachers tg ON cs.id_guru_mutlak = tg.id_guru
        ORDER BY c.nama_kelas, s.nama_mapel
    """)
    conn.close()
    return rows

@app.post("/api/allocations", response_model=ClassSubject)
def create_allocation(body: ClassSubjectCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak) VALUES (%s,%s,%s,%s) RETURNING id_class_subject",
            (body.id_kelas, body.id_mapel, body.durasi_jp, body.id_guru_mutlak)
        )
        conn.commit()
        new_id = cur.fetchone()["id_class_subject"]
        row = db_fetchone(conn, """
            SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
                   c.nama_kelas, s.nama_mapel, tg.nama_guru AS nama_guru_mutlak
            FROM   class_subjects cs
            JOIN   classes  c ON cs.id_kelas = c.id_kelas
            JOIN   subjects s ON cs.id_mapel  = s.id_mapel
            LEFT JOIN teachers tg ON cs.id_guru_mutlak = tg.id_guru
            WHERE  cs.id_class_subject = %s
        """, (new_id,))
        return row
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, "Mata pelajaran sudah dialokasikan untuk kelas ini!")
    finally:
        cur.close(); conn.close()

@app.delete("/api/allocations/{id_class_subject}")
def delete_allocation(id_class_subject: int):
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM class_subjects WHERE id_class_subject = %s", (id_class_subject,))
    conn.commit(); cur.close(); conn.close()
    return {"status": "SUCCESS", "message": "Alokasi berhasil dihapus"}

@app.patch("/api/allocations/{id_class_subject}")
def update_allocation(id_class_subject: int, body: AllocationUpdate):
    if body.durasi_jp <= 0 or body.durasi_jp > 40:
        raise HTTPException(400, "Durasi JP harus di antara 1 dan 40 JP")
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            UPDATE class_subjects 
            SET durasi_jp = %s, id_guru_mutlak = %s
            WHERE id_class_subject = %s 
            RETURNING id_class_subject
        """, (body.durasi_jp, body.id_guru_mutlak, id_class_subject))
        conn.commit()
        if not cur.fetchone():
            raise HTTPException(404, "Alokasi tidak ditemukan")
        return {"status": "SUCCESS", "message": "Alokasi berhasil diperbarui"}
    finally:
        cur.close(); conn.close()


@app.post("/api/allocations/copy")
def copy_allocations(body: AllocationCopy):
    id_asal = body.id_kelas_asal
    id_tujuan = body.id_kelas_tujuan
    if id_asal == id_tujuan:
        raise HTTPException(400, "Kelas asal dan kelas tujuan tidak boleh sama!")
    
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        # Check if source class exists
        cur.execute("SELECT id_kelas FROM classes WHERE id_kelas = %s", (id_asal,))
        if not cur.fetchone():
            raise HTTPException(404, "Kelas asal tidak ditemukan!")
        
        # Check if target class exists
        cur.execute("SELECT id_kelas FROM classes WHERE id_kelas = %s", (id_tujuan,))
        if not cur.fetchone():
            raise HTTPException(404, "Kelas tujuan tidak ditemukan!")
        
        # Get source allocations
        cur.execute("SELECT id_mapel, durasi_jp, id_guru_mutlak FROM class_subjects WHERE id_kelas = %s", (id_asal,))
        source_allocs = cur.fetchall()
        
        if not source_allocs:
            raise HTTPException(400, "Kelas asal tidak memiliki alokasi kurikulum!")
        
        # Clear existing allocations for target class
        cur.execute("DELETE FROM class_subjects WHERE id_kelas = %s", (id_tujuan,))
        
        # Insert duplicated allocations
        for alloc in source_allocs:
            cur.execute(
                "INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak) VALUES (%s, %s, %s, %s)",
                (id_tujuan, alloc["id_mapel"], alloc["durasi_jp"], alloc["id_guru_mutlak"])
            )
        conn.commit()
        return {"status": "SUCCESS", "message": f"Berhasil menyalin {len(source_allocs)} alokasi kurikulum."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal menyalin alokasi: {str(e)}")
    finally:
        cur.close(); conn.close()


# ═══════════════════════════════════════════════
#  CRUD - Teacher Subjects (Penugasan Guru)
# ═══════════════════════════════════════════════

@app.get("/api/teacher-subjects", response_model=List[TeacherSubject])
def get_teacher_subjects():
    conn = get_db_connection()
    rows = db_fetchall(conn, """
        SELECT ts.id_teacher_subject, ts.id_guru, ts.id_mapel,
               t.nama_guru, t.kode_guru, s.nama_mapel
        FROM   teacher_subjects ts
        JOIN   teachers t ON ts.id_guru  = t.id_guru
        JOIN   subjects s ON ts.id_mapel = s.id_mapel
        ORDER BY t.nama_guru, s.nama_mapel
    """)
    conn.close()
    return rows

@app.post("/api/teacher-subjects", response_model=TeacherSubject)
def create_teacher_subject(body: TeacherSubjectCreate):
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO teacher_subjects (id_guru, id_mapel) VALUES (%s,%s) RETURNING id_teacher_subject",
            (body.id_guru, body.id_mapel)
        )
        conn.commit()
        new_id = cur.fetchone()["id_teacher_subject"]
        row = db_fetchone(conn, """
            SELECT ts.id_teacher_subject, ts.id_guru, ts.id_mapel,
                   t.nama_guru, t.kode_guru, s.nama_mapel
            FROM   teacher_subjects ts
            JOIN   teachers t ON ts.id_guru  = t.id_guru
            JOIN   subjects s ON ts.id_mapel = s.id_mapel
            WHERE  ts.id_teacher_subject = %s
        """, (new_id,))
        return row
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(400, "Penugasan guru untuk mata pelajaran ini sudah ada!")
    finally:
        cur.close(); conn.close()

@app.delete("/api/teacher-subjects/{id_teacher_subject}")
def delete_teacher_subject(id_teacher_subject: int):
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM teacher_subjects WHERE id_teacher_subject = %s", (id_teacher_subject,))
    conn.commit(); cur.close(); conn.close()
    return {"status": "SUCCESS", "message": "Penugasan guru berhasil dihapus"}


# ═══════════════════════════════════════════════
#  Dashboard stats
# ═══════════════════════════════════════════════

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    try:
        n_t  = db_fetchone(conn, "SELECT COUNT(*) AS n FROM teachers")["n"]
        n_c  = db_fetchone(conn, "SELECT COUNT(*) AS n FROM classes")["n"]
        n_s  = db_fetchone(conn, "SELECT COUNT(*) AS n FROM subjects")["n"]
        n_a  = db_fetchone(conn, "SELECT COUNT(*) AS n FROM class_subjects")["n"]
        n_ts = db_fetchone(conn, "SELECT COUNT(*) AS n FROM teacher_subjects")["n"]
        n_tt = db_fetchone(conn, "SELECT COUNT(*) AS n FROM timetable")["n"]
        n_fb = db_fetchone(conn, "SELECT COUNT(*) AS n FROM timetable WHERE is_fallback = TRUE")["n"]
        return {
            "teachers":         n_t,
            "classes":          n_c,
            "subjects":         n_s,
            "allocations":      n_a,
            "teacher_subjects": n_ts,
            "timetable_slots":  n_tt,
            "fallback_count":   n_fb,
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════
#  Static files (frontend)
# ═══════════════════════════════════════════════

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
