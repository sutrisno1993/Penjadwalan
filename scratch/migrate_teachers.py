import pymysql
import json

ORIGINAL_MAPPING = {
    1: "REZA PATRIOTA PUTRA, S.Kom",
    2: "TAMAN SASTRA DIKARNA, S.Pd",
    3: "SUHARNO, S.Pdi",
    4: "SAMSUL HUDA, S.Pd",
    5: "AHMAD HUSEN NASUTION, SS",
    6: "WISNU NARA UTAMA, S.Pd",
    7: "FITRI MULYANI, S.Pd",
    8: "DERA ISMAWATI, S.PdI",
    9: "WIDONI SANTOSO, S.Pd",
    10: "SRI TITA MULYATI",
    11: "EUIS SUPRIHATIN, S.Pd",
    12: "WIDA HARTANI, S.Pd",
    13: "LUTHFI AHMAD NAZHIF, S.Pd",
    14: "WIDJAYANTI, S.Sos",
    15: "DEDE HIDAYATULLAH",
    16: "KOKO",
    17: "CHRISTIN SIREGAR, S.Pd",
    18: "Muhammad Syafe'i",
    19: "Muhammad Andika Prawira",
    20: "Dra. Sri Chandri Yani",
    21: "Yulistio",
    22: "Kuat Suparto",
    23: "Astri Wulandari",
    24: "Arief Akbar Fadillah",
    25: "Agung Ainul Hakim",
    26: "Sutrisno",
    27: "Muhammad Albar Sapin",
    28: "Tiara Shanti Hartono, S.Sos",
    29: "Oktari Qomimis Syatun, S.Pd",
    30: "Catur Wulandari",
    31: "Dwiana Rikasari, S.Ap",
    32: "IDAYATUL MUSTAFIDAH",
    33: "RISKA AMELIA, S.M",
    34: "SISTER NINDA PUTRI, S.Pd",
    35: "DELA AMELIA PUTRI, S.Pd",
    36: "WIWIK UMAYAH, S.Pd",
    37: "ENDANG KURNIAWAN, ST"
}

NEW_TEACHERS = [
    {"new_code": 1, "orig_code": 1, "new_name": "Reza Patriota Putra, S.Kom"},
    {"new_code": 2, "orig_code": 2, "new_name": "Taman Sastra Dikarna, S.Pd"},
    {"new_code": 3, "orig_code": 3, "new_name": "Suharno, S.Pdi"},
    {"new_code": 4, "orig_code": 4, "new_name": "Samsul Huda, S.Pd"},
    {"new_code": 5, "orig_code": 5, "new_name": "Ahmad Husen Nasution, Ss"},
    {"new_code": 6, "orig_code": 6, "new_name": "Wisnu Nara Utama, S.Pd"},
    {"new_code": 7, "orig_code": 7, "new_name": "Fitri Mulyani, S.Pd"},
    {"new_code": 8, "orig_code": 8, "new_name": "Dera Ismawati, A.Md"},
    {"new_code": 9, "orig_code": 9, "new_name": "Widoni Santoso, S.Pd"},
    {"new_code": 10, "orig_code": 10, "new_name": "Sri Tita Mulyati"},
    {"new_code": 11, "orig_code": 11, "new_name": "Euis Suprihatin, S.Pd"},
    {"new_code": 12, "orig_code": 12, "new_name": "Wida Hartani, S.Pd"},
    {"new_code": 13, "orig_code": 13, "new_name": "Luthfi Ahmad Nazhif, S.Pd"},
    {"new_code": 14, "orig_code": 14, "new_name": "Widjayanti, S.Sos"},
    {"new_code": 15, "orig_code": 15, "new_name": "Dede Hidayatullah"},
    {"new_code": 16, "orig_code": 16, "new_name": "Koko, ST"},
    {"new_code": 17, "orig_code": 17, "new_name": "Christin Siregar, S.Pd"},
    {"new_code": 18, "orig_code": 18, "new_name": "Muhammad Syafe'I"},
    {"new_code": 19, "orig_code": 19, "new_name": "M. Andika Prawira, S.Kom"},
    {"new_code": 20, "orig_code": 21, "new_name": "Yulistio Hardiyanto, ST"},
    {"new_code": 21, "orig_code": 22, "new_name": "Kuat Suparto, ST"},
    {"new_code": 22, "orig_code": 23, "new_name": "Astri Wulandari, S.Ak"},
    {"new_code": 23, "orig_code": 25, "new_name": "Agung Ainul Hakim"},
    {"new_code": 24, "orig_code": 26, "new_name": "Sutrisno"},
    {"new_code": 25, "orig_code": 27, "new_name": "Muhammad Albar Sapin, SM"},
    {"new_code": 26, "orig_code": 28, "new_name": "Tiara Shanti Hartono, S.Sos"},
    {"new_code": 27, "orig_code": 29, "new_name": "Oktari Qomimis Syatun, S.Pd"},
    {"new_code": 28, "orig_code": 30, "new_name": "Catur Wulandari, A.Md"},
    {"new_code": 29, "orig_code": 31, "new_name": "Dwiana Rikasari, S.Ap"},
    {"new_code": 30, "orig_code": 32, "new_name": "Idayatul Mustafidah, SE"},
    {"new_code": 31, "orig_code": 33, "new_name": "Riska Amelia, S.M"},
    {"new_code": 32, "orig_code": 34, "new_name": "Sister Ninda Putri, S.Pd"},
    {"new_code": 33, "orig_code": 35, "new_name": "Dela Amelia Putri, S.Pd"},
    {"new_code": 34, "orig_code": 36, "new_name": "Wiwik Umayah, S.Pd"},
    {"new_code": 35, "orig_code": 37, "new_name": "Endang Kurniawan, ST"},
    {"new_code": 36, "orig_code": None, "new_name": "Azmiral Azis, S.Pd"},
    {"new_code": 37, "orig_code": None, "new_name": "Muhammad Syachtiko, S.Pd"},
    {"new_code": 38, "orig_code": None, "new_name": "Fauzi, S.Kom"},
    {"new_code": 39, "orig_code": None, "new_name": "Septiani Raka Siwi, M.Pd"}
]

def migrate_db(db_name):
    print(f"\nMigrating database: {db_name}...")
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="")
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(f"USE {db_name}")
        
        # Step 1: Detect if database has been corrupted (swapped names)
        cur.execute("SELECT id_guru FROM teachers WHERE nama_guru LIKE '%Agung Ainul%' AND kode_guru = 23")
        is_corrupted = cur.fetchone() is not None
        
        if is_corrupted:
            print("  -> Database is in corrupted/swapped state. Restoring original names first...")
            for code, orig_name in ORIGINAL_MAPPING.items():
                cur.execute("UPDATE teachers SET nama_guru = %s WHERE kode_guru = %s", (orig_name, code))
            cur.execute("SELECT id_guru FROM teachers WHERE kode_guru > 37")
            new_ids = [row['id_guru'] for row in cur.fetchall()]
            if new_ids:
                placeholders = ", ".join(["%s"] * len(new_ids))
                cur.execute(f"DELETE FROM teacher_subjects WHERE id_guru IN ({placeholders})", tuple(new_ids))
                cur.execute(f"DELETE FROM teachers WHERE id_guru IN ({placeholders})", tuple(new_ids))
            print("  -> Original names restored successfully.")
            
        # Step 2: Set all kode_guru to negative to avoid UNIQUE constraint conflicts during update
        print("  -> Setting all kode_guru to negative values temporarily...")
        cur.execute("UPDATE teachers SET kode_guru = -kode_guru")
        
        # Step 3: Map each teacher by matching original code or name, and update to new code and new name and new WA
        ALL_DAYS = json.dumps(["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"])
        for t in NEW_TEACHERS:
            new_code = t["new_code"]
            orig_code = t["orig_code"]
            new_name = t["new_name"]
            no_wa = f"08123456{new_code:04d}"
            
            if orig_code is not None:
                cur.execute("SELECT id_guru FROM teachers WHERE kode_guru = %s", (-orig_code,))
                row = cur.fetchone()
                if row:
                    id_guru = row["id_guru"]
                    cur.execute("""
                        UPDATE teachers 
                        SET kode_guru = %s, nama_guru = %s, no_wa = %s
                        WHERE id_guru = %s
                    """, (new_code, new_name, no_wa, id_guru))
                    print(f"  -> Updated: {new_name} (Code: {new_code})")
                    continue
            
            cur.execute("SELECT id_guru FROM teachers WHERE nama_guru = %s", (new_name,))
            row = cur.fetchone()
            if row:
                id_guru = row["id_guru"]
                cur.execute("""
                    UPDATE teachers 
                    SET kode_guru = %s, no_wa = %s
                    WHERE id_guru = %s
                """, (new_code, no_wa, id_guru))
                print(f"  -> Updated (by name match): {new_name} (Code: {new_code})")
            else:
                cur.execute("""
                    INSERT INTO teachers 
                    (kode_guru, nama_guru, hari_tersedia, shift_pagi, shift_siang,
                     hari_tersedia_pagi, hari_tersedia_siang, no_wa)
                    VALUES (%s, %s, %s, TRUE, TRUE, %s, %s, %s)
                """, (new_code, new_name, ALL_DAYS, ALL_DAYS, ALL_DAYS, no_wa))
                print(f"  -> Inserted new: {new_name} (Code: {new_code})")
                
        # Step 4: Delete teachers who are still negative
        cur.execute("SELECT id_guru, nama_guru FROM teachers WHERE kode_guru < 0")
        to_delete = cur.fetchall()
        if to_delete:
            delete_ids = [row["id_guru"] for row in to_delete]
            delete_names = [row["nama_guru"] for row in to_delete]
            print(f"  -> Deleting old teachers not in list: {', '.join(delete_names)}")
            placeholders = ", ".join(["%s"] * len(delete_ids))
            cur.execute(f"DELETE FROM teacher_subjects WHERE id_guru IN ({placeholders})", tuple(delete_ids))
            cur.execute(f"DELETE FROM teachers WHERE id_guru IN ({placeholders})", tuple(delete_ids))
            
        conn.commit()
        print(f"Migration completed successfully for {db_name}!")
    except Exception as e:
        conn.rollback()
        print(f"ERROR migrating {db_name}: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate_db("jadwal_bekasi")
    migrate_db("jadwal_jakarta")
    migrate_db("lms_db")
