import sys
import re
import pymysql

sys.path.insert(0, 'd:/Jadwal')
from backend.seeder import SUBJECTS

def main():
    sql_path = "d:/Jadwal/backend/seed_class_subjects.sql"
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*([0-9]+|NULL)\s*,\s*([0-9]+)\s*\)"
    matches = re.findall(pattern, content)
    
    db_subjects = {s["nama_mapel"] for s in SUBJECTS}
    
    skipped_subjects = set()
    for match in matches:
        subject_name = match[1].strip()
        if subject_name not in db_subjects:
            skipped_subjects.add(subject_name)
            
    print("Skipped subjects in SQL seeder:")
    for s in sorted(list(skipped_subjects)):
        print(f"  - {s}")
        
if __name__ == '__main__':
    main()
