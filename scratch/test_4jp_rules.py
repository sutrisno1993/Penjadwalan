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
                
                # Check if it's consecutive or split
                # Let's check if there is a gap or a break
                # Break is after JP 4. So if JP 4 and JP 5 are both in the list, they are split by break.
                # Let's reconstruct the periods
                periods_str = ", ".join([f"Jam-{p}" for p in jps])
                mapels_str = " & ".join(mapels)
                
                is_multi = len(mapels) > 1
                if is_multi:
                    multi_mapel_4jp += 1
                    status = "[OK] MULTI-MAPEL (Sangat Baik/Diutamakan)"
                else:
                    single_mapel_4jp += 1
                    # Check if it's split by break or other means
                    # Since JP 1-4 is the only block without break, check if it is exactly JP 1, 2, 3, 4
                    if jps == [1, 2, 3, 4]:
                        status = "[ERR] SEKAT GAGAL: Berturut-turut Jam 1-4 tanpa sekat!"
                    else:
                        # Check for gaps or if it crosses JP 4/5 boundary
                        has_break_split = 4 in jps and 5 in jps
                        has_gap_split = any(jps[i+1] - jps[i] > 1 for i in range(len(jps)-1))
                        if has_break_split or has_gap_split:
                            status = "[OK] SINGLE-MAPEL (Berhasil disekat istirahat/jeda)"
                        else:
                            status = "[WARN] SINGLE-MAPEL (Berurutan but not 1-4? check slots)"

                print(f"- Guru: {teacher_name:<30} | Kelas: {class_name:<10} | Hari: {day:<7} | Total: {jp_count} JP")
                print(f"  Mapel: {mapels_str}")
                print(f"  Jam  : {periods_str}")
                print(f"  Status: {status}\n")

        print("----------------------------------------------------------------------")
        print(f"Total Kasus Mengajar >= 4 JP: {total_4jp_instances}")
        print(f"  - Multi-Mapel             : {multi_mapel_4jp}")
        print(f"  - Single-Mapel (disekat)  : {single_mapel_4jp}")
        print("----------------------------------------------------------------------")

    finally:
        conn.close()

if __name__ == '__main__':
    run_test()
