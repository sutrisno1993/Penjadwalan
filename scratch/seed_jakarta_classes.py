import sys
sys.path.insert(0, 'd:/Jadwal')
from dotenv import load_dotenv
load_dotenv('d:/Jadwal/.env')

from backend.database import get_db_connection, active_branch

def main():
    # Set active_branch ContextVar to 'jakarta' so get_db_connection connects to the jakarta schema!
    active_branch.set("jakarta")
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        print("Membersihkan kelas lama di cabang Jakarta...")
        # Restarts sequence to 1, uses CASCADE to clean child relations
        cur.execute("TRUNCATE TABLE classes RESTART IDENTITY CASCADE;")
        
        levels = ["X", "XI", "XII"]
        majors_config = {
            "MP": 2,
            "AKL": 1,
            "TKJ": 4
        }
        
        inserted_count = 0
        for lvl in levels:
            # Shift logic: XI is SIANG, others (X, XII) are PAGI
            shift = "SIANG" if lvl == "XI" else "PAGI"
            
            for major, count in majors_config.items():
                for idx in range(1, count + 1):
                    nama_kelas = f"{lvl} {major} {idx}"
                    cur.execute(
                        """
                        INSERT INTO classes (nama_kelas, shift_operasional, tingkat, jurusan)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (nama_kelas) DO NOTHING;
                        """,
                        (nama_kelas, shift, lvl, major)
                    )
                    inserted_count += 1
                    print(f"Tersimpan: {nama_kelas} | Shift: {shift} | Tingkat: {lvl} | Jurusan: {major}")
                    
        conn.commit()
        print(f"Sukses! Berhasil menanamkan {inserted_count} kelas di skema cabang Jakarta.")
    except Exception as e:
        conn.rollback()
        print(f"Gagal melakukan seeding kelas Jakarta: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
