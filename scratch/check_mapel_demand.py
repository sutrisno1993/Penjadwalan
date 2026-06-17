import os
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()

def check_mapel_demand():
    conn = get_db_connection()
    try:
        # Get all allocations and group by mapel
        rows = db_fetchall(conn, """
            SELECT s.nama_mapel, s.id_mapel, SUM(cs.durasi_jp) as total_jp, COUNT(cs.id_class_subject) as n_classes
            FROM class_subjects cs
            JOIN subjects s ON cs.id_mapel = s.id_mapel
            GROUP BY s.nama_mapel, s.id_mapel
            ORDER BY total_jp DESC
        """)
        
        print("=== MAPEL DEMAND VS TEACHER CAPACITY ===")
        for r in rows:
            mid = r['id_mapel']
            mname = r['nama_mapel']
            demand = r['total_jp']
            
            # Find qualified teachers
            teachers = db_fetchall(conn, """
                SELECT t.id_guru, t.nama_guru, t.max_jp
                FROM teacher_subjects ts
                JOIN teachers t ON ts.id_guru = t.id_guru
                WHERE ts.id_mapel = %s
            """, (mid,))
            
            t_names = [f"{t['nama_guru']} (max {t['max_jp'] or 60} JP)" for t in teachers]
            total_cap = sum(t['max_jp'] if t['max_jp'] is not None else 60 for t in teachers)
            
            print(f"Mapel: {mname} | Demand: {demand} JP ({r['n_classes']} kelas)")
            print(f"  Qualified Teachers (Total Cap: {total_cap} JP):")
            for t in t_names:
                print(f"    - {t}")
            if total_cap < demand:
                print(f"    ⚠️ CAPACITY DEFICIT! Demand {demand} > Capacity {total_cap}")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check_mapel_demand()
