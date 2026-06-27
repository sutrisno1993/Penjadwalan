import sys
import os
import json
import ssl
import datetime
import urllib.request
import urllib.error
from urllib.parse import urlparse

# Set project root path
sys.path.insert(0, 'd:/Jadwal')

from backend.database import get_db_connection, db_fetchall, get_setting, active_branch

def default_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def normalize_lms_url(raw_url: str) -> str:
    """
    Menormalisasi URL agar selalu mengarah ke endpoint /api/v1/sync-all.
    Mengatasi kasus jika user memasukkan domain utama atau URL login admin.
    """
    raw_url = raw_url.strip()
    if not raw_url:
        return ""
    
    parsed = urlparse(raw_url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc
    
    # Jika user tidak memasukkan scheme (misal: bekasi.lms11maret.xyz/login/admin)
    if not netloc and parsed.path:
        parts = parsed.path.split('/')
        netloc = parts[0]
        
    return f"{scheme}://{netloc}/api/v1/sync-all"

def test_sync(branch_name="bekasi"):
    print(f"=== Memulai Uji Coba Sinkronisasi ke VPS (Cabang: {branch_name.upper()}) ===")
    
    active_branch.set(branch_name)
    conn = get_db_connection()
    try:
        # 1. Baca URL dan API Key
        raw_url = get_setting("lms_api_url", "").strip()
        lms_key = get_setting("lms_api_key", "").strip()
        
        print(f"URL di Pengaturan: '{raw_url}'")
        print(f"API Key: '{lms_key[:5]}...' jika ada" if lms_key else "API Key: Kosong/Belum diset")
        
        if not raw_url:
            print("PANDUAN: Silakan isi lms_api_url di UI Pengaturan terlebih dahulu.")
            return False
            
        # 2. Normalisasi URL
        normalized_url = normalize_lms_url(raw_url)
        print(f"Hasil URL Normalisasi (Target API): '{normalized_url}'")
        
        # 3. Muat Data Ringan (Hanya 1 data per tabel untuk uji coba koneksi)
        print("Membaca data lokal...")
        teachers = db_fetchall(conn, "SELECT * FROM teachers LIMIT 2")
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
            
        classes = db_fetchall(conn, "SELECT nama_kelas, shift_operasional, tingkat, jurusan FROM classes LIMIT 2")
        subjects = db_fetchall(conn, "SELECT nama_mapel, kategori_mapel, tingkat, jurusan FROM subjects LIMIT 2")
        
        teacher_subjects = db_fetchall(conn, """
            SELECT t.kode_guru, s.nama_mapel
            FROM teacher_subjects ts
            JOIN teachers t ON ts.id_guru = t.id_guru
            JOIN subjects s ON ts.id_mapel = s.id_mapel
            LIMIT 2
        """)
        
        class_subjects = db_fetchall(conn, """
            SELECT c.nama_kelas, s.nama_mapel, cs.durasi_jp, t.kode_guru AS kode_guru_mutlak
            FROM class_subjects cs
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            LEFT JOIN teachers t ON cs.id_guru_mutlak = t.id_guru
            LIMIT 2
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
            LIMIT 2
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
        
        # 4. Kirim ke VPS
        print("Mengirim payload uji coba ke VPS...")
        
        # Siapkan context SSL unverified untuk bypass sertifikat SSL
        ctx = ssl._create_unverified_context()
        
        req = urllib.request.Request(
            normalized_url,
            data=json.dumps(payload, default=default_serializer).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {lms_key}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                print("\n=== RESPON DARI VPS ===")
                print(res_body)
                print("=======================")
                print("KESIMPULAN: Koneksi dan pengiriman data ke VPS SUKSES!")
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"\n[HTTP ERROR] Kode: {e.code}")
            print(f"Respon Error: {err_body}")
            print("KESIMPULAN: Terhubung ke VPS tetapi server Laravel menolak data (cek API key atau kecocokan skema database VPS).")
            return False
        except urllib.error.URLError as e:
            print(f"\n[CONNECTION ERROR] Gagal menghubungi VPS: {e.reason}")
            print("KESIMPULAN: Gagal menghubungi server VPS (cek koneksi internet, firewall port, atau alamat domain).")
            return False
        except Exception as e:
            print(f"\n[UNKNOWN ERROR] Terjadi kesalahan: {e}")
            return False
            
    finally:
        conn.close()

if __name__ == "__main__":
    # Secara default uji cabang bekasi. Bisa diubah ke jakarta jika diperlukan
    branch = "bekasi"
    if len(sys.argv) > 1:
        branch = sys.argv[1]
    test_sync(branch)
