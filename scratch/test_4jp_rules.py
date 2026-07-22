import sys
import os
import json
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall
from backend.solver import generate_timetable

def run_test():
    print("Running solver to generate a fresh timetable...")
    res = generate_timetable()
    print(f"Solver result: {res['status']}")
    if res['status'] != 'SUCCESS':
        print(f"Errors: {res.get('errors')}")
        print(f"Warnings: {res.get('warnings')}")
        return

    conn = get_db_connection()
    try:
        # Fetch timetable and join with class_subjects and teachers to check
        schedule = db_fetchall(conn, """
            SELECT t.hari, t.jam_ke, t.id_guru, tg.nama_guru, cs.id_kelas, c.nama_kelas, cs.id_mapel, m.nama_mapel
            FROM timetable t
            JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
            JOIN classes c ON cs.id_kelas = c.id_kelas
            JOIN teachers tg ON t.id_guru = tg.id_guru
            JOIN subjects m ON cs.id_mapel = m.id_mapel
            ORDER BY tg.nama_guru, c.nama_kelas, t.hari, t.jam_ke
        """)

        # Group by (teacher_name, class_name, day) to find who teaches 4 JP
        grouped = {}
        for entry in schedule:
            key = (entry['nama_guru'], entry['nama_kelas'], entry['hari'])
            grouped.setdefault(key, []).append(entry)

        # Group by (class_name, mapel_name, day) to verify 3 JP limit per mapel
        mapel_day_group = {}
        for entry in schedule:
            key = (entry['nama_kelas'], entry['nama_mapel'], entry['hari'])
            mapel_day_group.setdefault(key, []).append(entry)

        print("\n--- VERIFIKASI BATASAN KERAS 3 JP PER MAPEL PER HARI ---")
        violations_3jp_limit = 0
        for key, entries in mapel_day_group.items():
            duration = len(entries)
            if duration > 3:
                violations_3jp_limit += 1
                class_name, mapel_name, day = key
                print(f"[ERR] Pelanggaran Batas 3 JP Mapel: Kelas {class_name} | Mapel {mapel_name} | Hari {day} | Durasi {duration} JP")
        if violations_3jp_limit == 0:
            print("[OK] Tidak ada pelanggaran batas 3 JP per mapel per hari!")
        else:
            print(f"[ERR] Terdeteksi {violations_3jp_limit} pelanggaran batas 3 JP per mapel!")

        print("\n--- ANALISIS GURU MENGAJAR 4 JP ATAU LEBIH DI SATU KELAS PADA SATU HARI ---")
        total_4jp_instances = 0
        single_mapel_4jp = 0
        multi_mapel_4jp = 0

        for key, entries in grouped.items():
            jp_count = len(entries)
            if jp_count >= 4:
                total_4jp_instances += 1
                teacher_name, class_name, day = key
                jps = sorted([e['jam_ke'] for e in entries])
                mapels = list(set([e['nama_mapel'] for e in entries]))
                
                periods_str = ", ".join([f"Jam-{p}" for p in jps])
                mapels_str = " & ".join(mapels)
                
                is_multi = len(mapels) > 1
                if is_multi:
                    multi_mapel_4jp += 1
                    status = "[OK] MULTI-MAPEL (Sangat Baik/Diutamakan)"
                else:
                    single_mapel_4jp += 1
                    # Since single mapel is now capped at 3 JP, this should theoretically be impossible to reach 4 JP!
                    status = "[ERR] SINGLE-MAPEL (Melanggar batas 3 JP per mapel!)"

                print(f"- Guru: {teacher_name:<30} | Kelas: {class_name:<10} | Hari: {day:<7} | Total: {jp_count} JP")
                print(f"  Mapel: {mapels_str}")
                print(f"  Jam  : {periods_str}")
                print(f"  Status: {status}\n")

        print("----------------------------------------------------------------------")
        print(f"Total Kasus Mengajar >= 4 JP: {total_4jp_instances}")
        print(f"  - Multi-Mapel             : {multi_mapel_4jp}")
        print(f"  - Single-Mapel (4 JP)     : {single_mapel_4jp}")
        print("----------------------------------------------------------------------")

    finally:
        conn.close()

if __name__ == '__main__':
    run_test()
