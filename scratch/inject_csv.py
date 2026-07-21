import csv
import sys
import os

# Add parent to path to allow importing backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import get_db_connection, clear_master_data, active_branch
def normalize_class(class_name):
    # AP -> OTKP
    class_name = class_name.replace(" AP ", " OTKP ")
    # AK -> AKL
    class_name = class_name.replace(" AK ", " AKL ")
    return class_name.strip()

def run_injection(csv_path):
    print("Setting active branch to jakarta...")
    active_branch.set("jakarta")
    print("Clearing old master data...")
    clear_master_data()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            teacher_name = row['Nama Guru'].strip()
            subject_name = row['Mata Pelajaran'].strip()
            class_name = normalize_class(row['Kelas'].strip())
            durasi_jp = int(row['Jam per Minggu'].strip())
            
            kode_guru = int(row['No'].strip()) if row.get('No') and row['No'].strip().isdigit() else 0
            if not teacher_name or not subject_name or not class_name:
                continue

            # 1. Get/Insert Teacher
            cur.execute("SELECT id_guru FROM teachers WHERE nama_guru = %s", (teacher_name,))
            teacher = cur.fetchone()
            if not teacher:
                # Default shift_pagi=1, shift_siang=1, max_jp=60, hari_tersedia='["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'
                hari = '["SENIN","SELASA","RABU","KAMIS","JUMAT","SABTU"]'
                cur.execute(
                    "INSERT INTO teachers (kode_guru, nama_guru, shift_pagi, shift_siang, max_jp, hari_tersedia) VALUES (%s, %s, %s, %s, %s, %s)",
                    (kode_guru, teacher_name, 1, 1, 60, hari)
                )
                id_guru = cur.lastrowid
            else:
                id_guru = teacher['id_guru']

            # 2. Get/Insert Class
            cur.execute("SELECT id_kelas FROM classes WHERE nama_kelas = %s", (class_name,))
            cls = cur.fetchone()
            if not cls:
                # Guess shift based on some logic, or default to PAGI
                shift = "PAGI"
                cur.execute(
                    "INSERT INTO classes (nama_kelas, shift_operasional) VALUES (%s, %s)",
                    (class_name, shift)
                )
                id_kelas = cur.lastrowid
            else:
                id_kelas = cls['id_kelas']

            # 3. Get/Insert Subject
            cur.execute("SELECT id_mapel FROM subjects WHERE nama_mapel = %s", (subject_name,))
            subj = cur.fetchone()
            if not subj:
                kategori_mapel = "UMUM"
                if "Penjas" in subject_name or "PJOK" in subject_name:
                    kategori_mapel = "OLAHRAGA"
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
            
            # 5. Insert Class-Subject (Allocation) and set id_guru_mutlak
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
                # Update existing allocation to use this teacher as mutlak
                cur.execute(
                    "UPDATE class_subjects SET durasi_jp = %s, id_guru_mutlak = %s WHERE id_class_subject = %s",
                    (durasi_jp, id_guru, alloc['id_class_subject'])
                )
                
    conn.commit()
    conn.close()
    print("Injection complete!")

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'd:/Jadwal/data_alokasi_guru_percord copy.csv'
    run_injection(csv_path)
