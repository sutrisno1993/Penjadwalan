import sys
import os
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import parse_allocations

def main():
    allocations = parse_allocations()
    md_classes = sorted(list({a["class"] for a in allocations}))
    
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("USE jadwal_bekasi")
    cur.execute("SELECT nama_kelas FROM classes")
    db_classes = sorted([row["nama_kelas"] for row in cur.fetchall()])
    cur.close()
    conn.close()
    
    print("Classes in Markdown:")
    print(md_classes)
    print("\nClasses in DB:")
    print(db_classes)
    
if __name__ == '__main__':
    main()
