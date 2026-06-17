import os
import logging
from dotenv import load_dotenv
from backend.database import get_db_connection, db_fetchall

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_subjects")

MAP = {
    "Pendidikan Agama Islam": "Pendidikan Agama dan Budi Pekerti",
    "PPKn": "Pendidikan Pancasila dan Kewarganegaraan",
    "Penjasorkes": "Pendidikan Jasmani, Olah Raga & Kesehatan",
    "PKK": "Produk Kreatif dan Kewirausahaan",
    "Spreadsheet": "Aplikasi Pengolah Angka / Spreadsheet",
    "TDO": "Teknik Dasar Otomotif",
    "PDTO": "Pengerjaan Dasar Teknik Otomotif",
    "Adm Pajak": "Administrasi Pajak",
    "Adm Umum": "Administrasi Umum",
    "Adm. Umum": "Administrasi Umum",
    "OTK Humas": "Administrasi Humas dan Keprotokolan",
    "OTK Humas dan Keprotokolan": "Administrasi Humas dan Keprotokolan",
    "OTK Kepegawaian": "Administrasi Kepegawaian",
    "OTK Keuangan": "Administrasi Keuangan",
    "OTK Sarpras": "Administrasi Sarana dan Prasarana",
    "AK Lembaga": "Praktikum Akuntansi Lembaga / Instansi Pemerintah",
    "AK Keuangan": "Akuntansi Keuangan",
    "KKA / Coding": "Mapel Pilihan (KKA / Coding)",
    "Wide Area Network (WAN)": "Teknologi Jaringan Berbasis WAN",
    "Teknik Infrastruktur Jaringan": "Teknologi Infrastruktur Jaringan",
    "Adm Sistem Jaringan": "Administrasi Sistem Jaringan",
    "Tek Jaringan Komputer": "Teknologi Jaringan Komputer",
    "Tek Layanan Jaringan": "Teknologi Layanan Jaringan",
    "Main. Mesin Kendaraan": "Pemeliharaan Mesin Kendaraan Ringan",
    "Main. Mesin Sepeda Motor": "Pemeliharaan Mesin Sepeda Motor",
    "Main. Sasis Kendaraan": "Pemeliharaan Sasis dan Pemindah Tenaga Kendaraan Ringan",
    "Main. Sasis Sepeda Motor": "Pemeliharaan Sasis Sepeda Motor",
    "Kelistrikan Kendaraan Ringan": "Pemeliharaan Kelistrikan Kendaraan Ringan",
    "Kelistrikan Sepeda Motor": "Pemeliharaan Kelistrikan Sepeda Motor",
    "Kelistrikan Kendaraan": "Pemeliharaan Kelistrikan Kendaraan Ringan" # Map any other occurrences
}

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get all subjects
        subjects = db_fetchall(conn, "SELECT id_mapel, nama_mapel FROM subjects")
        sub_dict = {s["nama_mapel"]: s["id_mapel"] for s in subjects}

        for short_name, long_name in MAP.items():
            if short_name not in sub_dict:
                continue
            
            id_short = sub_dict[short_name]
            
            if long_name in sub_dict:
                id_long = sub_dict[long_name]
                logger.info(f"Merging '{short_name}' (id: {id_short}) into '{long_name}' (id: {id_long})")
                
                # 1. Update teacher_subjects
                # Fetch all teachers qualified for the short subject
                ts_entries = db_fetchall(conn, "SELECT id_guru, id_teacher_subject FROM teacher_subjects WHERE id_mapel = %s", (id_short,))
                for ts in ts_entries:
                    id_guru = ts["id_guru"]
                    id_ts = ts["id_teacher_subject"]
                    
                    # Check if already qualified for the long subject
                    exists = db_fetchall(conn, "SELECT 1 FROM teacher_subjects WHERE id_guru = %s AND id_mapel = %s", (id_guru, id_long))
                    if exists:
                        # Already exists, delete the duplicate short one
                        cur.execute("DELETE FROM teacher_subjects WHERE id_teacher_subject = %s", (id_ts,))
                    else:
                        # Update to point to long subject
                        cur.execute("UPDATE teacher_subjects SET id_mapel = %s WHERE id_teacher_subject = %s", (id_long, id_ts))
                
                # 2. Update class_subjects (allocations)
                cs_entries = db_fetchall(conn, "SELECT id_kelas, id_class_subject, durasi_jp FROM class_subjects WHERE id_mapel = %s", (id_short,))
                for cs in cs_entries:
                    id_kelas = cs["id_kelas"]
                    id_cs = cs["id_class_subject"]
                    durasi = cs["durasi_jp"]
                    
                    # Check if already exists for the long subject
                    exists = db_fetchall(conn, "SELECT id_class_subject, durasi_jp FROM class_subjects WHERE id_kelas = %s AND id_mapel = %s", (id_kelas, id_long))
                    if exists:
                        # Merge the durations or keep max (we update the long one and delete the short one)
                        new_durasi = max(durasi, exists[0]["durasi_jp"])
                        cur.execute("UPDATE class_subjects SET durasi_jp = %s WHERE id_class_subject = %s", (new_durasi, exists[0]["id_class_subject"]))
                        cur.execute("DELETE FROM class_subjects WHERE id_class_subject = %s", (id_cs,))
                    else:
                        # Update to point to long subject
                        cur.execute("UPDATE class_subjects SET id_mapel = %s WHERE id_class_subject = %s", (id_long, id_cs))
                
                # 3. Delete from subjects
                cur.execute("DELETE FROM subjects WHERE id_mapel = %s", (id_short,))
                
            else:
                # Long name doesn't exist, just rename short name to long name
                logger.info(f"Renaming '{short_name}' (id: {id_short}) to '{long_name}'")
                cur.execute("UPDATE subjects SET nama_mapel = %s WHERE id_mapel = %s", (long_name, id_short))
                sub_dict[long_name] = id_short
                
        conn.commit()
        logger.info("Successfully merged/cleaned up duplicate and abbreviated subject names.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error merging subjects: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
