"""
debug_guru.py - Diagnosa data guru IDAYATUL
"""
import os, json
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from backend.database import get_db_connection, db_fetchall, db_fetchone

conn = get_db_connection()

# 1. Cari guru IDAYATUL
print("=" * 60)
print("1. DATA GURU - IDAYATUL")
print("=" * 60)
rows = db_fetchall(conn, "SELECT * FROM teachers WHERE UPPER(nama_guru) LIKE '%IDAYATUL%'")
for r in rows:
    r["hari_tersedia"]       = json.loads(r.get("hari_tersedia") or "[]")
    r["hari_tersedia_pagi"]  = json.loads(r.get("hari_tersedia_pagi") or "[]")
    r["hari_tersedia_siang"] = json.loads(r.get("hari_tersedia_siang") or "[]")
    print(f"  id_guru         : {r['id_guru']}")
    print(f"  nama_guru       : {r['nama_guru']}")
    print(f"  kode_guru       : {r['kode_guru']}")
    print(f"  shift_pagi      : {r['shift_pagi']}")
    print(f"  shift_siang     : {r['shift_siang']}")
    print(f"  hari_tersedia_pagi  : {r['hari_tersedia_pagi']}")
    print(f"  hari_tersedia_siang : {r['hari_tersedia_siang']}")
    guru_id = r['id_guru']

# 2. Cari mapel spreadsheet
print()
print("=" * 60)
print("2. MAPEL - SPREADSHEET")
print("=" * 60)
mapels = db_fetchall(conn, "SELECT * FROM subjects WHERE UPPER(nama_mapel) LIKE '%SPREADSHEET%' OR UPPER(nama_mapel) LIKE '%PENGOLAH ANGKA%'")
for m in mapels:
    print(f"  id_mapel      : {m['id_mapel']}")
    print(f"  nama_mapel    : {m['nama_mapel']}")
    print(f"  kategori      : {m['kategori_mapel']}")
    print(f"  tingkat       : {m['tingkat']}")
    print(f"  jurusan       : {m['jurusan']}")

# 3. Cek penugasan guru → mapel
print()
print("=" * 60)
print("3. PENUGASAN GURU (teacher_subjects) untuk IDAYATUL")
print("=" * 60)
if rows:
    guru_id = rows[0]['id_guru']
    ts = db_fetchall(conn, """
        SELECT ts.*, s.nama_mapel, s.kategori_mapel
        FROM teacher_subjects ts
        JOIN subjects s ON ts.id_mapel = s.id_mapel
        WHERE ts.id_guru = %s
    """, (guru_id,))
    if ts:
        for t in ts:
            print(f"  id_teacher_subject : {t['id_teacher_subject']}")
            print(f"  id_mapel           : {t['id_mapel']}")
            print(f"  nama_mapel         : {t['nama_mapel']}")
    else:
        print("  !! TIDAK ADA penugasan ditemukan untuk guru ini !!")

# 4. Cek kelas X AK 1
print()
print("=" * 60)
print("4. KELAS - X AK 1")
print("=" * 60)
kelas = db_fetchall(conn, "SELECT * FROM classes WHERE UPPER(nama_kelas) LIKE '%X AK%'")
for k in kelas:
    print(f"  id_kelas          : {k['id_kelas']}")
    print(f"  nama_kelas        : {k['nama_kelas']}")
    print(f"  shift_operasional : {k['shift_operasional']}")

# 5. Cek alokasi mapel spreadsheet di kelas X AK 1
print()
print("=" * 60)
print("5. ALOKASI - Spreadsheet di kelas X AK")
print("=" * 60)
alok = db_fetchall(conn, """
    SELECT cs.*, c.nama_kelas, c.shift_operasional, s.nama_mapel
    FROM class_subjects cs
    JOIN classes  c ON cs.id_kelas = c.id_kelas
    JOIN subjects s ON cs.id_mapel = s.id_mapel
    WHERE UPPER(s.nama_mapel) LIKE '%SPREADSHEET%' OR UPPER(s.nama_mapel) LIKE '%PENGOLAH ANGKA%'
""")
for a in alok:
    print(f"  kelas  : {a['nama_kelas']} ({a['shift_operasional']})")
    print(f"  mapel  : {a['nama_mapel']}")
    print(f"  JP/mgu : {a['durasi_jp']}")
    print()

conn.close()
print("=" * 60)
print("SELESAI DIAGNOSA")
print("=" * 60)
