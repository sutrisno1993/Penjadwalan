import csv
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection, clear_master_data, active_branch

SUBJECT_MAP = {
    'PAI': 'Pendidikan Agama Islam',
    'Pend. Agama Islam': 'Pendidikan Agama Islam',
    'PPkn': 'PPKn',
    'Sejarah': 'Sejarah Indonesia',
    'Adm Sistem Jaringan': 'Administrasi Sistem Jaringan',
    'Tek Layanan Jaringan': 'Teknologi Layanan Jaringan',
    'Tek Perkantoran': 'Teknologi Perkantoran',
    'Tek Jaringan Komp': 'Teknologi Jaringan Komputer',
    'Tek Insfr Jaringan': 'Administrasi Infrastruktur Jaringan',
    'Dasar Komp Jaringan': 'Dasar Komputer dan Jaringan',
    'AK Dasar': 'Akuntansi Dasar',
    'AK Keuangan': 'Akuntansi Keuangan',
    'AK Lembaga': 'Akuntansi Lembaga',
    'AK Manufaktur': 'Praktikum Akuntansi Perusahaan Jasa, Dagang dan Manufaktur',
    'Adm. Pajak': 'Adm Pajak',
    'Bisnis Tek Informasi': 'Bisnis Teknologi Informasi',
}

def normalize_class(class_name):
    # AP -> OTKP
    class_name = class_name.replace(" AP ", " OTKP ")
    # AK -> AKL
    class_name = class_name.replace(" AK ", " AKL ")
    return class_name.strip()

def normalize_subject(subject_name):
    s = subject_name.strip()
    return SUBJECT_MAP.get(s, s)

def run_injection(csv_path):
    print("Clearing old master data in database specified by .env...")
    clear_master_data()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        inserted_rows = 0
        for row in reader:
            raw_no = row.get('No', '').strip()
            teacher_name = row['Nama Guru'].strip()
            subject_name = normalize_subject(row['Mata Pelajaran'])
            class_name = normalize_class(row['Kelas'])
            durasi_jp = int(row['Jam per Minggu'].strip())
            
            kode_guru = int(raw_no) if raw_no.isdigit() else 0
            if not teacher_name or not subject_name or not class_name:
                continue

            # 1. Get or Insert Teacher
            cur.execute("SELECT id_guru FROM teachers WHERE kode_guru = %s OR nama_guru = %s", (kode_guru, teacher_name))
            teacher = cur.fetchone()
            if not teacher:
                hari = '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'
                cur.execute(
                    "INSERT INTO teachers (kode_guru, nama_guru, shift_pagi, shift_siang, max_jp, hari_tersedia) VALUES (%s, %s, %s, %s, %s, %s)",
                    (kode_guru, teacher_name, 1, 1, 60, hari)
                )
                id_guru = cur.lastrowid
            else:
                id_guru = teacher['id_guru']

            # 2. Get or Insert Class
            cur.execute("SELECT id_kelas FROM classes WHERE nama_kelas = %s", (class_name,))
            cls = cur.fetchone()
            if not cls:
                shift = "SIANG" if ("XI " in class_name or "XII " in class_name) else "PAGI"
                cur.execute(
                    "INSERT INTO classes (nama_kelas, shift_operasional) VALUES (%s, %s)",
                    (class_name, shift)
                )
                id_kelas = cur.lastrowid
            else:
                id_kelas = cls['id_kelas']

            # 3. Get or Insert Subject
            cur.execute("SELECT id_mapel FROM subjects WHERE nama_mapel = %s", (subject_name,))
            subj = cur.fetchone()
            if not subj:
                kategori_mapel = "UMUM"
                if "Penjas" in subject_name or "PJOK" in subject_name:
                    kategori_mapel = "OLAHRAGA"
                elif any(x in subject_name for x in ["AK", "OTK", "Tek", "Adm", "Spreadsheet", "PKK", "Kearsipan", "Korespondensi", "WAN", "Photoshop", "Accurate"]):
                    kategori_mapel = "PRODUKTIF"

                cur.execute(
                    "INSERT INTO subjects (nama_mapel, kategori_mapel) VALUES (%s, %s)",
                    (subject_name, kategori_mapel)
                )
                id_mapel = cur.lastrowid
            else:
                id_mapel = subj['id_mapel']

            # 4. Link Teacher-Subject
            cur.execute(
                "SELECT id_teacher_subject FROM teacher_subjects WHERE id_guru = %s AND id_mapel = %s",
                (id_guru, id_mapel)
            )
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO teacher_subjects (id_guru, id_mapel) VALUES (%s, %s)",
                    (id_guru, id_mapel)
                )

            # 5. Insert Class-Subject (Allocation)
            cur.execute(
                "SELECT id_class_subject FROM class_subjects WHERE id_kelas = %s AND id_mapel = %s",
                (id_kelas, id_mapel)
            )
            alloc = cur.fetchone()
            if not alloc:
                cur.execute(
                    "INSERT INTO class_subjects (id_kelas, id_mapel, durasi_jp, id_guru_mutlak) VALUES (%s, %s, %s, %s)",
                    (id_kelas, id_mapel, durasi_jp, id_guru)
                )
            else:
                cur.execute(
                    "UPDATE class_subjects SET durasi_jp = %s, id_guru_mutlak = %s WHERE id_class_subject = %s",
                    (durasi_jp, id_guru, alloc['id_class_subject'])
                )

            inserted_rows += 1

    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    conn.close()
    print(f"Injection complete! Total {inserted_rows} allocation records inserted into 'jakarta' database.")

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'd:/Jadwal/data_alokasi_guru_percord.csv'
    run_injection(csv_file)
