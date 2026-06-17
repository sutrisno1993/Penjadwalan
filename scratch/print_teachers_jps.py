from backend.database import get_db_connection
from dotenv import load_dotenv

def main():
    load_dotenv()
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_guru, nama_guru, kode_guru, min_jp, max_jp FROM teachers ORDER BY nama_guru")
    teachers = cur.fetchall()
    
    print("=== TEACHERS JP LIMITS ===")
    for t in teachers:
        if t['min_jp'] is not None or t['max_jp'] is not None:
            print(f"ID: {t['id_guru']} | Guru: {t['nama_guru']} (Kode: {t['kode_guru']}) | Min JP: {t['min_jp']} | Max JP: {t['max_jp']}")
            
    conn.close()

if __name__ == '__main__':
    main()
