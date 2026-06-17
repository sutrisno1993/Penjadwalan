import time
import json
from backend.database import get_db_connection
from backend.main import DAYS_ORDER

def measure():
    t0 = time.time()
    conn = get_db_connection()
    t1 = time.time()
    print(f"Connection took: {t1 - t0:.4f}s")
    
    # Measure each query
    q_times = {}
    
    q = "SELECT id_kelas, nama_kelas, shift_operasional FROM classes"
    start = time.time()
    cur = conn.cursor()
    cur.execute(q)
    classes = cur.fetchall()
    q_times['classes'] = time.time() - start
    
    q = "SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, hari_tersedia_pagi, hari_tersedia_siang, min_jp, max_jp FROM teachers"
    start = time.time()
    cur.execute(q)
    teachers = cur.fetchall()
    q_times['teachers'] = time.time() - start
    
    q = "SELECT id_mapel, nama_mapel, kategori_mapel FROM subjects"
    start = time.time()
    cur.execute(q)
    subjects = cur.fetchall()
    q_times['subjects'] = time.time() - start
    
    q = """
        SELECT cs.id_class_subject, cs.id_kelas, cs.id_mapel, cs.durasi_jp,
               c.nama_kelas, c.shift_operasional, s.nama_mapel, s.kategori_mapel
        FROM   class_subjects cs
        JOIN   classes  c ON cs.id_kelas = c.id_kelas
        JOIN   subjects s ON cs.id_mapel  = s.id_mapel
    """
    start = time.time()
    cur.execute(q)
    allocations = cur.fetchall()
    q_times['allocations'] = time.time() - start
    
    q = "SELECT id_guru, id_mapel FROM teacher_subjects"
    start = time.time()
    cur.execute(q)
    ts_rows = cur.fetchall()
    q_times['teacher_subjects'] = time.time() - start
    
    print("Query timings:")
    for name, elapsed in q_times.items():
        print(f"  {name}: {elapsed:.4f}s")
        
    start_calc = time.time()
    # parse JSON fields
    for t in teachers:
        t["hari_tersedia_pagi"]  = json.loads(t["hari_tersedia_pagi"]  or "[]")
        t["hari_tersedia_siang"] = json.loads(t["hari_tersedia_siang"] or "[]")
        t["shift_pagi"]  = bool(t["shift_pagi"])
        t["shift_siang"] = bool(t["shift_siang"])
        # wait, let's see if allowed_jp_pagi exists in dict
        t["allowed_jp_pagi"]     = json.loads(t["allowed_jp_pagi"])     if t.get("allowed_jp_pagi")     else None
        t["allowed_jp_siang"]    = json.loads(t["allowed_jp_siang"])    if t.get("allowed_jp_siang")    else None
        
    teachers_map = {t["id_guru"]: t for t in teachers}
    
    # 1. Daily Coverage Map
    daily_coverage = []
    for shift in ["PAGI", "SIANG"]:
        n_kelas = sum(1 for c in classes if c["shift_operasional"] == shift)
        for day in DAYS_ORDER:
            guru_hadir = []
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
    subject_demand = {}
    subject_classes = {}
    for a in allocations:
        mid = a["id_mapel"]
        subject_demand[mid] = subject_demand.get(mid, 0) + a["durasi_jp"]
        subject_classes.setdefault(mid, []).append(a["nama_kelas"])
        
    subject_teachers = {}
    for ts in ts_rows:
        mid = ts["id_mapel"]
        gid = ts["id_guru"]
        if gid in teachers_map:
            subject_teachers.setdefault(mid, []).append(teachers_map[gid])
            
    for s in subjects:
        mid = s["id_mapel"]
        demand = subject_demand.get(mid, 0)
        if demand == 0:
            continue
            
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
            status = "RED"
        elif total_capacity < demand:
            status = "RED"
        elif demand > 0.85 * total_capacity:
            status = "YELLOW"
        else:
            status = "GREEN"
            
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
    
    print(f"Calculations took: {time.time() - start_calc:.4f}s")
    print(f"Total logic took: {time.time() - t0:.4f}s")
    
    conn.close()

if __name__ == '__main__':
    measure()
