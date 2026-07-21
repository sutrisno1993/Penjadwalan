import json
from backend.database import set_thread_branch, get_db_connection, db_fetchall

set_thread_branch('bekasi')
conn = get_db_connection()

print("==================================================")
print(" 1. GURU DENGAN KETERSEDIAAN HARI SANGAT KETAT (< 3 HARI)")
print("==================================================")
teachers = db_fetchall(conn, "SELECT id_guru, kode_guru, nama_guru, hari_tersedia_pagi, hari_tersedia_siang FROM teachers")
ketat_count = 0
for t in teachers:
    try:
        hp = json.loads(t['hari_tersedia_pagi']) if t['hari_tersedia_pagi'] else []
        hs = json.loads(t['hari_tersedia_siang']) if t['hari_tersedia_siang'] else []
    except Exception:
        hp, hs = [], []
    total_days = set(hp + hs)
    if len(total_days) > 0 and len(total_days) < 3:
        ketat_count += 1
        print(f"- [Guru {t['kode_guru']}] {t['nama_guru']}: Pagi={hp}, Siang={hs} (Total: {len(total_days)} hari)")

if ketat_count == 0:
    print("Tidak ada guru dengan ketersediaan < 3 hari.")

print("\n==================================================")
print(" 2. GURU DENGAN BEBAN JP TINGGI VS HARI TERSEDIA")
print("==================================================")
# Check total JP taught by each teacher vs available days
alloc_rows = db_fetchall(conn, """
    SELECT cs.id_class_subject, cs.durasi_jp, cs.id_guru_mutlak, ts.id_guru
    FROM class_subjects cs
    LEFT JOIN teacher_subjects ts ON cs.id_mapel = ts.id_mapel
""")
guru_jp = {}
for r in alloc_rows:
    gid = r['id_guru_mutlak'] or r['id_guru']
    if gid:
        guru_jp[gid] = guru_jp.get(gid, 0) + r['durasi_jp']

for t in teachers:
    gid = t['id_guru']
    jp = guru_jp.get(gid, 0)
    try:
        hp = json.loads(t['hari_tersedia_pagi']) if t['hari_tersedia_pagi'] else []
        hs = json.loads(t['hari_tersedia_siang']) if t['hari_tersedia_siang'] else []
    except Exception:
        hp, hs = [], []
    num_days = len(set(hp + hs))
    if jp > 0 and num_days > 0:
        max_capacity = num_days * 6 # max 6 JP per hari
        if jp > max_capacity:
            print(f"- OVERLOAD: [Guru {t['kode_guru']}] {t['nama_guru']} memikul {jp} JP, tapi hanya tersedia {num_days} hari (Kapasitas maks: {max_capacity} JP)!")

print("\n==================================================")
print(" 3. ALOKASI KELAS-MAPEL DENGAN JP SANGAT TINGGI (>= 4 JP)")
print("==================================================")
high_jp = db_fetchall(conn, """
    SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak, g.nama_guru AS nama_guru_mutlak
    FROM class_subjects cs
    JOIN classes c ON cs.id_kelas = c.id_kelas
    JOIN subjects s ON cs.id_mapel = s.id_mapel
    LEFT JOIN teachers g ON cs.id_guru_mutlak = g.id_guru
    WHERE cs.durasi_jp >= 4
    ORDER BY cs.durasi_jp DESC
""")
print(f"Total alokasi >= 4 JP: {len(high_jp)} alokasi")
for h in high_jp[:10]:
    mutlak_str = f" [Guru Mutlak: {h['nama_guru_mutlak']}]" if h['id_guru_mutlak'] else ""
    print(f"- Kelas {h['nama_kelas']} - {h['nama_mapel']}: {h['durasi_jp']} JP/minggu{mutlak_str}")

print("\n==================================================")
print(" 4. CEK BATAS MAX JP IDEAL & DARURAT SETTINGS")
print("==================================================")
from backend.database import get_setting
max_ideal = get_setting('max_jp_ideal', '3')
max_darurat = get_setting('max_jp_darurat', '4')
print(f"Batas Max JP Ideal saat ini: {max_ideal} JP/hari")
print(f"Batas Max JP Darurat saat ini: {max_darurat} JP/hari")

conn.close()
