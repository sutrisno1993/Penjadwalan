import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.database import get_db_connection, active_branch, db_fetchall
from backend.main import update_teachers_availability, get_teachers, TeacherAvailabilityBatchItem

def test_save():
    token = active_branch.set("jakarta")
    conn = get_db_connection()
    t = db_fetchall(conn, "SELECT id_guru, nama_guru, hari_tersedia_pagi, hari_tersedia_siang FROM teachers WHERE kode_guru=5")[0]
    conn.close()
    
    print("Initial Teacher 5 in Jakarta:", t)
    
    item = TeacherAvailabilityBatchItem(
        id_guru=t["id_guru"],
        hari_tersedia_pagi=["SENIN", "SELASA", "RABU", "KAMIS"],
        hari_tersedia_siang=["SENIN", "SELASA", "RABU", "KAMIS"]
    )
    
    res = update_teachers_availability([item])
    print("Update result:", res)
    
    teachers_after = get_teachers()
    t5 = next(x for x in teachers_after if x["id_guru"] == t["id_guru"])
    print("Teacher 5 after update (via get_teachers):")
    print("  hari_tersedia:", t5["hari_tersedia"])
    print("  hari_tersedia_pagi:", t5["hari_tersedia_pagi"])
    print("  hari_tersedia_siang:", t5["hari_tersedia_siang"])
    
    assert t5["hari_tersedia_pagi"] == ["SENIN", "SELASA", "RABU", "KAMIS"]
    assert t5["hari_tersedia_siang"] == ["SENIN", "SELASA", "RABU", "KAMIS"]
    assert t5["hari_tersedia"] == ["SENIN", "SELASA", "RABU", "KAMIS"]
    
    print("\nTEST PASSED SUCCESSFULLY!")
    active_branch.reset(token)

if __name__ == "__main__":
    test_save()
