import subprocess

blob_db_py = "f30bc1f1fa04632e05c81d239bf45cb554db8983"

print("Restoring backend/database.py from blob", blob_db_py[:8])
db_content = subprocess.check_output(['git', 'cat-file', '-p', blob_db_py]).decode('utf-8')
with open(r'd:\Jadwal_BKS\backend\database.py', 'w', encoding='utf-8') as f:
    f.write(db_content)

print("=== backend/database.py RESTORED SUCCESSFULLY ===")
