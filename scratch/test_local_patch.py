import sys
sys.path.insert(0, 'd:/Jadwal')

from backend.main import update_class
from backend.models import ClassCreate

def test():
    try:
        body = ClassCreate(
            nama_kelas="X TSM 2",
            shift_operasional="SIANG",
            tingkat="X",
            jurusan="TSM"
        )
        
        import pymysql
        conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("USE jadwal_bekasi")
        cur.execute("SELECT id_kelas FROM classes WHERE nama_kelas = 'X TSM 2'")
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            print("Class not found in DB!")
            return
            
        id_kelas = row["id_kelas"]
        print(f"Running update_class local test for ID {id_kelas}...")
        
        res = update_class(id_kelas, body)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test()
