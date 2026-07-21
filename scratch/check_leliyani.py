import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.database import get_db_connection, active_branch, db_fetchall

for branch in ["bekasi", "jakarta"]:
    token = active_branch.set(branch)
    conn = get_db_connection()
    rows = db_fetchall(conn, "SELECT id_guru, nama_guru, kode_guru, shift_pagi, shift_siang, hari_tersedia, hari_tersedia_pagi, hari_tersedia_siang FROM teachers WHERE nama_guru LIKE '%LELIYANI%' OR kode_guru=25")
    conn.close()
    active_branch.reset(token)
    print(f"=== BRANCH {branch.upper()} ===")
    for r in rows:
        print(r)
