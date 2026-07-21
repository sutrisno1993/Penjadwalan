import sys
import os
import json
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, db_fetchall, db_execute
from backend.solver import generate_timetable

def run_test():
    print("Connecting to DB...")
    conn = get_db_connection()
    try:
        # 1. Ambil salah satu guru, misal nama 'Catur' atau guru pertama
        teachers = db_fetchall(conn, "SELECT * FROM teachers ORDER BY id_guru")
        if not teachers:
            print("ERROR: Tidak ada guru di database.")
            return
        
        target_teacher = None
        for t in teachers:
            if "catur" in t["nama_guru"].lower():
                target_teacher = t
                break
        if not target_teacher:
            target_teacher = teachers[0]
            
        print(f"Menggunakan guru uji: {target_teacher['nama_guru']} (ID: {target_teacher['id_guru']})")
        
        # Simpan state awal untuk dikembalikan nanti
        orig_pagi = target_teacher.get("allowed_jp_pagi")
        orig_siang = target_teacher.get("allowed_jp_siang")
        
        # --- Fase 1: Uji Baseline (Tanpa Batasan Baru) ---
        print("\n--- FASE 1: Menguji Kelayakan Baseline (Tanpa Batasan) ---")
        db_execute(
            conn, 
            "UPDATE teachers SET allowed_jp_pagi = NULL, allowed_jp_siang = NULL WHERE id_guru = %s",
            (target_teacher['id_guru'],)
        )
        conn.commit()
        
        baseline_res = generate_timetable()
        print(f"Status Baseline: {baseline_res['status']}")
        if baseline_res['status'] != 'SUCCESS':
            print("Peringatan: Baseline saat ini sudah tidak layak/feasible! Error:", baseline_res.get("errors"))
            print("Mencoba membersihkan batasan dan memulihkan...")
            # Restore and exit
            db_execute(
                conn, 
                "UPDATE teachers SET allowed_jp_pagi = %s, allowed_jp_siang = %s WHERE id_guru = %s",
                (json.dumps(orig_pagi) if orig_pagi else None, json.dumps(orig_siang) if orig_siang else None, target_teacher['id_guru'])
            )
            conn.commit()
            return
            
        # --- Fase 2: Uji Dengan Batasan JP (Blokir JP 7) ---
        print("\n--- FASE 2: Menguji Dengan Batasan JP (Blokir JP 7 untuk Senin-Jumat) ---")
        # Kita hanya izinkan JP 1 s.d. 6 (blokir JP 7)
        jp_restrictions = {
            "SENIN": [1, 2, 3, 4, 5, 6],
            "SELASA": [1, 2, 3, 4, 5, 6],
            "RABU": [1, 2, 3, 4, 5, 6],
            "KAMIS": [1, 2, 3, 4, 5, 6],
            "JUMAT": [1, 2, 3, 4, 5, 6]
        }
        
        db_execute(
            conn, 
            "UPDATE teachers SET allowed_jp_pagi = %s, allowed_jp_siang = NULL WHERE id_guru = %s",
            (json.dumps(jp_restrictions), target_teacher['id_guru'])
        )
        conn.commit()
        
        res = generate_timetable()
        print(f"Status Solver dengan Batasan: {res['status']}")
        
        if res['status'] != 'SUCCESS':
            print("Solver Gagal dengan batasan tersebut. Error:", res.get("errors"))
            print("Mungkin memblokir JP 7 membuat sistem infeasible karena beban guru ini terlalu tinggi.")
        else:
            # Ambil jadwal dari database untuk verifikasi
            schedule = db_fetchall(conn, """
                SELECT t.hari, t.jam_ke, t.id_guru, cs.id_kelas, c.shift_operasional
                FROM timetable t
                JOIN class_subjects cs ON t.id_class_subject = cs.id_class_subject
                JOIN classes c ON cs.id_kelas = c.id_kelas
                WHERE t.id_guru = %s OR t.original_guru_id = %s
            """, (target_teacher['id_guru'], target_teacher['id_guru']))
            
            print(f"Ditemukan {len(schedule)} entri jadwal untuk guru {target_teacher['nama_guru']}.")
            
            violations = 0
            for entry in schedule:
                hari = entry['hari'].upper()
                jp = entry['jam_ke']
                shift = entry['shift_operasional']
                if shift == "PAGI" and hari in jp_restrictions:
                    allowed = jp_restrictions[hari]
                    if jp not in allowed:
                        print(f"PELANGGARAN: Dijadwalkan pada {hari} JP {jp} (Harusnya hanya boleh {allowed})")
                        violations += 1
                    else:
                        print(f"OK: Dijadwalkan pada {hari} JP {jp} (Dalam batas boleh {allowed})")
                else:
                    print(f"INFO: Dijadwalkan pada {hari} JP {jp} (Shift {shift}, tidak terikat batasan JP pagi)")
                    
            if violations == 0:
                print("\n>>> VERIFIKASI BERHASIL! OR-Tools menghormati batasan JP guru. <<<")
            else:
                print(f"\n>>> VERIFIKASI GAGAL! Ditemukan {violations} pelanggaran. <<<")
                
        # 5. Kembalikan ke original state
        print("\nMengembalikan data guru ke semula...")
        db_execute(
            conn, 
            "UPDATE teachers SET allowed_jp_pagi = %s, allowed_jp_siang = %s WHERE id_guru = %s",
            (orig_pagi, orig_siang, target_teacher['id_guru'])
        )
        conn.commit()
        
    finally:
        conn.close()

if __name__ == "__main__":
    run_test()
