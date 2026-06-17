"""
Script diagnosa: cek apakah guru sudah ditugaskan untuk mapel Aplikasi Pengolah Angka
dan apakah shift_pagi sudah diset TRUE.
"""
import json
import sys
sys.path.insert(0, 'd:/Jadwal')

from backend.database import get_db_connection, db_fetchall, db_fetchone

conn = get_db_connection()

# 1. Cari mapel Aplikasi Pengolah Angka / Spreadsheet
mapel_list = db_fetchall(conn, """
    SELECT * FROM subjects
    WHERE LOWER(nama_mapel) LIKE '%angka%'
       OR LOWER(nama_mapel) LIKE '%spreadsheet%'
       OR LOWER(nama_mapel) LIKE '%aplikasi%'
""")
print("=== MAPEL DITEMUKAN ===")
if not mapel_list:
    print("  [TIDAK ADA] Mapel tidak ditemukan!")
for m in mapel_list:
    print(f"  id={m['id_mapel']}, nama={m['nama_mapel']}, kategori={m['kategori_mapel']}")

if not mapel_list:
    conn.close()
    sys.exit()

id_mapel = mapel_list[0]['id_mapel']
print(f"\n  -> Menggunakan id_mapel = {id_mapel}")

# 2. Cek teacher_subjects untuk mapel ini
ts = db_fetchall(conn, """
    SELECT ts.id_guru, ts.id_mapel, t.nama_guru, t.shift_pagi, t.shift_siang,
           t.hari_tersedia_pagi, t.hari_tersedia_siang
    FROM teacher_subjects ts
    JOIN teachers t ON ts.id_guru = t.id_guru
    WHERE ts.id_mapel = %s
""", (id_mapel,))

print(f"\n=== PENUGASAN GURU (teacher_subjects) UNTUK MAPEL ID={id_mapel} ===")
if not ts:
    print("  !! KOSONG !! Belum ada relasi di teacher_subjects untuk mapel ini.")
    print("  >> Ini kemungkinan PENYEBAB error. Tambahkan penugasan guru di Tab 5.")
for row in ts:
    sp = bool(row['shift_pagi'])
    ss = bool(row['shift_siang'])
    print(f"  Guru: {row['nama_guru']}")
    print(f"    shift_pagi  = {sp}  | shift_siang = {ss}")
    hp = row['hari_tersedia_pagi'] or '[]'
    hs = row['hari_tersedia_siang'] or '[]'
    print(f"    hari_pagi   = {hp}")
    print(f"    hari_siang  = {hs}")
    if not sp:
        print(f"    !! MASALAH: shift_pagi=False — guru ini tidak akan lolos filter shift PAGI!")

# 3. Cek kelas X AK 1
kelas_list = db_fetchall(conn, """
    SELECT * FROM classes
    WHERE UPPER(nama_kelas) LIKE '%AK%1%'
       OR nama_kelas = 'X AK 1'
""")
print(f"\n=== KELAS X AK ===")
for k in kelas_list:
    print(f"  id={k['id_kelas']}, nama={k['nama_kelas']}, shift={k['shift_operasional']}")

# 4. Cek alokasi class_subjects untuk kelas X AK 1
for k in kelas_list:
    if 'AK 1' in k['nama_kelas'].upper():
        alloc = db_fetchall(conn, """
            SELECT cs.*, s.nama_mapel FROM class_subjects cs
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            WHERE cs.id_kelas = %s AND cs.id_mapel = %s
        """, (k['id_kelas'], id_mapel))
        print(f"\n=== ALOKASI [{k['nama_kelas']}] UNTUK MAPEL ===")
        if not alloc:
            print("  Tidak ada alokasi mapel ini untuk kelas ini.")
        for a in alloc:
            print(f"  id_class_subject={a['id_class_subject']}, durasi_jp={a['durasi_jp']}")

conn.close()
print("\n=== SELESAI ===")
