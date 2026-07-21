import re

with open('d:/Jadwal/jadwal_bekasi (1).sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract INSERT INTO teachers
teachers = re.findall(r"INSERT INTO `teachers`.*?VALUES\s*(.*?);", content, re.DOTALL)
classes = re.findall(r"INSERT INTO `classes`.*?VALUES\s*(.*?);", content, re.DOTALL)

print("=== CLASSES IN JADWAL_BEKASI (1).SQL ===")
if classes:
    for cl in classes[0].split("),"):
        print(cl.strip()[:100])

print("\n=== TEACHERS IN JADWAL_BEKASI (1).SQL ===")
if teachers:
    for t in teachers[0].split("),")[:10]:
        print(t.strip()[:100])
