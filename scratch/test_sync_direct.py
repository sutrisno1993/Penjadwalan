import sys
sys.path.insert(0, 'd:/Jadwal')
import json
import traceback
from backend.database import get_db_connection, db_fetchall, get_setting

def run_sync():
    conn = get_db_connection()
    try:
        lms_url = get_setting("lms_api_url", "").strip()
        lms_key = get_setting("lms_api_key", "").strip()
        print(f"LMS URL: {lms_url}, Key: {lms_key}")
        
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
        
        print("Data loaded! Sending to LMS...")
        import urllib.request, urllib.error
        req = urllib.request.Request(
            lms_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {lms_key}'
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                print(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"LMS Server Error: {e.code}\n{err_body}")
        except Exception as e:
            print(f"Other Error: {e}")
            
    except Exception as e:
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    run_sync()
