import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.database import get_db_connection, active_branch, db_fetchall

def inspect():
    for branch in ["bekasi", "jakarta"]:
        token = active_branch.set(branch)
        conn = get_db_connection()
        teachers = db_fetchall(conn, "SELECT id_guru, kode_guru, nama_guru, hari_tersedia, hari_tersedia_pagi, hari_tersedia_siang FROM teachers LIMIT 5")
        conn.close()
        print(f"=== Cabang {branch} ===")
        for t in teachers:
            print(t)
        active_branch.reset(token)

if __name__ == "__main__":
    inspect()
