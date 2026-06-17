import os
from dotenv import load_dotenv
from backend.solver import generate_timetable
from backend.database import get_db_connection

load_dotenv()

print("=== Mulai Generate ===")
result = generate_timetable()

print(f"\n=== Hasil ===")
print(f"Status: {result.get('status')}")
if result.get('status') != 'SUCCESS':
    print(f"Pesan Error: {result.get('message')}")
    print(f"Detail Error: {result.get('errors')}")

if result.get('warnings'):
    print(f"\nWarnings: {result.get('warnings')}")

if result.get('status') == 'SUCCESS':
    print(f"\n=== Rincian Guru yang Dipilih ===")
    conn = get_db_connection()
    try:
        rows = conn.cursor().execute("""
            SELECT g.nama_guru, COUNT(*) as n_jp
            FROM timetable t
            JOIN teachers g ON t.id_guru = g.id_guru
            GROUP BY g.nama_guru
            ORDER BY n_jp DESC
        """).fetchall()
        for row in rows:
            print(f"{row['nama_guru']}: {row['n_jp']} JP")
    finally:
        conn.close()
