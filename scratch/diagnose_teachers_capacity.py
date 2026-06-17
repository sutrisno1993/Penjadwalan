from backend.database import get_db_connection
from dotenv import load_dotenv
import json

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Load teachers
    cur.execute("SELECT id_guru, nama_guru, kode_guru, min_jp, max_jp FROM teachers")
    teachers = cur.fetchall()
    
    # 2. Load teacher subjects
    cur.execute("SELECT id_guru, id_mapel FROM teacher_subjects")
    ts = cur.fetchall()
    ts_map = {} # guru_id -> set of mapel_id
    mapel_teachers = {} # mapel_id -> list of guru_id
    for r in ts:
        ts_map.setdefault(r["id_guru"], set()).add(r["id_mapel"])
        mapel_teachers.setdefault(r["id_mapel"], []).append(r["id_guru"])
        
    # 3. Load allocations
    cur.execute("""
        SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp, cs.id_guru_mutlak,
               c.nama_kelas, s.nama_mapel
        FROM class_subjects cs
        JOIN classes c ON cs.id_kelas = c.id_kelas
        JOIN subjects s ON cs.id_mapel = s.id_mapel
    """)
    allocations = cur.fetchall()
    
    # Calculate demand per mapel
    mapel_demand = {}
    mapel_details = {}
    for a in allocations:
        mid = a["id_mapel"]
        mapel_demand[mid] = mapel_demand.get(mid, 0) + a["durasi_jp"]
        mapel_details[mid] = a["nama_mapel"]
        
    print("=== GLOBAL TEACHER CAPACITY DIAGNOSTIC ===")
    
    # Check A: For each teacher, what is the total JP of subjects where they are the ONLY qualified teacher?
    print("\n[A] Guru yang merupakan SATU-SATUNYA pengampu untuk mapel tertentu:")
    for t in teachers:
        tid = t["id_guru"]
        t_mapels = ts_map.get(tid, set())
        
        only_teacher_mapels = []
        only_teacher_jp = 0
        for mid in t_mapels:
            teachers_for_mid = mapel_teachers.get(mid, [])
            if len(teachers_for_mid) == 1 and teachers_for_mid[0] == tid:
                demand = mapel_demand.get(mid, 0)
                if demand > 0:
                    only_teacher_mapels.append(f"{mapel_details[mid]} ({demand} JP)")
                    only_teacher_jp += demand
                    
        max_jp = t["max_jp"] if t["max_jp"] is not None else 60
        min_jp = t["min_jp"] if t["min_jp"] is not None else 0
        
        if only_teacher_jp > max_jp:
            print(f"  ❌ {t['nama_guru']} (Kode: {t['kode_guru']}):")
            print(f"     Wajib mengajar: {only_teacher_jp} JP (karena satu-satunya pengampu untuk: {', '.join(only_teacher_mapels)})")
            print(f"     Batas Maksimal (max_jp): {max_jp} JP!")
            print(f"     KONDISI INI DIJAMIN MEMBUAT SOLVER INFEASIBLE!")
        elif only_teacher_jp > 0:
            print(f"  - {t['nama_guru']}: Wajib mengajar {only_teacher_jp} JP (max_jp: {max_jp})")

    # Check B: Check teachers who are locked as Guru Mutlak (id_guru_mutlak)
    print("\n[B] Guru Mutlak locked allocations:")
    for t in teachers:
        tid = t["id_guru"]
        locked_allocs = [a for a in allocations if a["id_guru_mutlak"] == tid]
        if locked_allocs:
            locked_jp = sum(a["durasi_jp"] for a in locked_allocs)
            max_jp = t["max_jp"] if t["max_jp"] is not None else 60
            if locked_jp > max_jp:
                print(f"  ❌ {t['nama_guru']} (Kode: {t['kode_guru']}):")
                print(f"     Terkunci secara mutlak untuk: {locked_jp} JP")
                print(f"     Batas Maksimal (max_jp): {max_jp} JP!")
                print(f"     KONDISI INI DIJAMIN MEMBUAT SOLVER INFEASIBLE!")
            else:
                print(f"  - {t['nama_guru']}: Terkunci mutlak {locked_jp} JP (max_jp: {max_jp})")

    conn.close()

if __name__ == '__main__':
    main()
