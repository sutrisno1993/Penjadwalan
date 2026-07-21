import sys
import os
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import parse_allocations, SUBJECTS

FUZZY_SUBJECT_MAP = {
    "Pendidikan Agama dan Budi Pekerti": "Pendidikan Agama Islam",
    "Pendidikan Pancasila dan Kewarganegaraan": "PPKn",
    "Pendidikan Jasmani, Olah Raga & Kesehatan": "Penjasorkes",
    "Teknologi Infrastruktur Jaringan": "Teknik Infrastruktur Jaringan",
    "Teknologi Layanan Jaringan": "Tek Layanan Jaringan",
    "Administrasi Sistem Jaringan": "Adm Sistem Jaringan",
    "AK Manufaktur": "Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur",
    "BAHASA INGGRIS": "Bahasa Inggris",
    "Informatik": "Informatika",
    "Pend Agama Islam": "Pendidikan Agama Islam",
    "Sejarah": "Sejarah Indonesia",
    "Tek Insfrs Jaringan": "Teknik Infrastruktur Jaringan",
    "WAN": "Wide Area Network (WAN)"
}

def map_class_name(cname):
    cname = cname.replace("AKL", "AK")
    cname = cname.replace("TBSM", "TSM")
    cname = cname.replace("TKRO", "TKR")
    return cname

def main():
    allocations = parse_allocations()
    db_subjects = {s["nama_mapel"] for s in SUBJECTS}
    
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("USE jadwal_bekasi")
    cur.execute("SELECT nama_kelas FROM classes")
    db_classes = {row["nama_kelas"] for row in cur.fetchall()}
    cur.close()
    conn.close()
    
    missing_classes = set()
    missing_subjects = set()
    
    for a in allocations:
        mapped_class = map_class_name(a["class"])
        if mapped_class not in db_classes:
            missing_classes.add(a["class"])
            
        subject_name = a["subject"]
        if subject_name in FUZZY_SUBJECT_MAP:
            subject_name = FUZZY_SUBJECT_MAP[subject_name]
            
        if subject_name not in db_subjects:
            missing_subjects.add(a["subject"])
            
    print("Missing classes:")
    print(sorted(list(missing_classes)))
    print("\nMissing subjects:")
    print(sorted(list(missing_subjects)))

if __name__ == '__main__':
    main()
