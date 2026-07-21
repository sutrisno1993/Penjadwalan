import re

with open('backend/main.py', encoding='utf-8') as f:
    lines = f.read()

# 1. create_teacher
lines = re.sub(r'RETURNING id_guru\s*\"\"\"', r'\"\"\"', lines)
lines = re.sub(r'new_id = cur\.fetchone\(\)\["id_guru"\]', r'new_id = cur.lastrowid', lines)

# 2. create_class
lines = re.sub(r'RETURNING id_kelas"', r'"', lines)
lines = re.sub(r'new_id = cur\.fetchone\(\)\["id_kelas"\]', r'new_id = cur.lastrowid', lines)

# 3. update_class
lines = re.sub(r'WHERE id_kelas=%s RETURNING id_kelas"', r'WHERE id_kelas=%s"', lines)
lines = re.sub(r'if not cur\.fetchone\(\):\s*raise HTTPException\(404, "Kelas tidak ditemukan"\)', r'', lines)

# 4. create_subject
lines = re.sub(r'RETURNING id_mapel"', r'"', lines)
lines = re.sub(r'new_id = cur\.fetchone\(\)\["id_mapel"\]', r'new_id = cur.lastrowid', lines)

# 5. update_subject
lines = re.sub(r'WHERE id_mapel=%s RETURNING id_mapel"', r'WHERE id_mapel=%s"', lines)
lines = re.sub(r'if not cur\.fetchone\(\):\s*raise HTTPException\(404, "Mata pelajaran tidak ditemukan"\)', r'', lines)

# 6. create_allocation
lines = re.sub(r'RETURNING id_class_subject"', r'"', lines)
lines = re.sub(r'new_id = cur\.fetchone\(\)\["id_class_subject"\]', r'new_id = cur.lastrowid', lines)

# 7. update_allocation
lines = re.sub(r'RETURNING id_class_subject\s*\"\"\"', r'\"\"\"', lines)
lines = re.sub(r'if not cur\.fetchone\(\):\s*raise HTTPException\(404, "Alokasi tidak ditemukan"\)', r'', lines)

# 8. create_teacher_subject
lines = re.sub(r'RETURNING id_teacher_subject"', r'"', lines)
lines = re.sub(r'new_id = cur\.fetchone\(\)\["id_teacher_subject"\]', r'new_id = cur.lastrowid', lines)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(lines)

print("Done fixing RETURNING syntax")
