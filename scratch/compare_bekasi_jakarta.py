import pymysql

def main():
    print("--- REAL BEKASI DATABASE ---")
    cb = pymysql.connect(host='127.0.0.1', user='root', password='', database='jadwal_bekasi', cursorclass=pymysql.cursors.DictCursor).cursor()
    cb.execute("""
        SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak, t.nama_guru 
        FROM class_subjects cs 
        JOIN classes c ON cs.id_kelas=c.id_kelas 
        JOIN subjects s ON cs.id_mapel=s.id_mapel 
        LEFT JOIN teachers t ON cs.id_guru_mutlak=t.id_guru 
        WHERE c.nama_kelas='X AKL 1'
    """)
    for r in cb.fetchall():
        print(r)

    print("\n--- REAL JAKARTA DATABASE ---")
    cj = pymysql.connect(host='127.0.0.1', user='root', password='', database='jadwal_jakarta', cursorclass=pymysql.cursors.DictCursor).cursor()
    cj.execute("""
        SELECT cs.id_class_subject, c.nama_kelas, s.nama_mapel, cs.durasi_jp, cs.id_guru_mutlak, t.nama_guru 
        FROM class_subjects cs 
        JOIN classes c ON cs.id_kelas=c.id_kelas 
        JOIN subjects s ON cs.id_mapel=s.id_mapel 
        LEFT JOIN teachers t ON cs.id_guru_mutlak=t.id_guru 
        WHERE c.nama_kelas='X AKL 1'
    """)
    for r in cj.fetchall():
        print(r)

if __name__ == '__main__':
    main()
