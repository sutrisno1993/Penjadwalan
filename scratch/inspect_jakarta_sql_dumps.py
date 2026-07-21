import re

for filename in ['d:/Jadwal/jadwal_jakarta.sql', 'd:/Jadwal/jadwal_jakarta_import.sql']:
    print(f"=== CHECKING {filename} ===")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        teachers = re.findall(r"INSERT INTO `teachers`.*?VALUES\s*(.*?);", content, re.DOTALL)
        if teachers:
            for t in teachers[0].split("),")[:5]:
                print(t.strip()[:150])
        else:
            print("No INSERT INTO teachers found.")
    except Exception as e:
        print(f"Error: {e}")
    print()
