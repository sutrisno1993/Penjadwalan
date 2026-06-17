from backend.database import get_db_connection
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    subject_ids = [95, 52, 53, 26, 27]
    for sid in subject_ids:
        cur.execute("SELECT nama_mapel FROM subjects WHERE id_mapel = %s", (sid,))
        sname = cur.fetchone()["nama_mapel"]
        
        cur.execute("""
            SELECT t.id_guru, t.nama_guru, t.max_jp
            FROM teacher_subjects ts
            JOIN teachers t ON ts.id_guru = t.id_guru
            WHERE ts.id_mapel = %s
        """, (sid,))
        teachers = cur.fetchall()
        
        print(f"\nSubject ID {sid}: {sname}")
        for t in teachers:
            print(f"  - Teacher: {t['nama_guru']} (ID: {t['id_guru']}, Max JP: {t['max_jp']})")
            
    conn.close()

if __name__ == '__main__':
    main()
