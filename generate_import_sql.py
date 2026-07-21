import os, re, sys

src_path = r"d:\\Jadwal\\jadwal_jakarta.sql"
import_path = r"d:\\Jadwal\\jadwal_jakarta_import.sql"

if not os.path.exists(src_path):
    print('Source SQL not found')
    sys.exit(1)

with open(src_path, "r", encoding="utf-8", errors="ignore") as src, open(import_path, "w", encoding="utf-8") as out:
    for line in src:
        # Transform CREATE TABLE
        if re.match(r"^CREATE TABLE `?\w+`?", line, re.IGNORECASE):
            line = line.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
        # Transform INSERT INTO
        if re.match(r"^INSERT INTO `?\w+`?", line, re.IGNORECASE):
            # Insert IGNORE after INSERT
            line = line.replace("INSERT INTO", "INSERT IGNORE INTO")
        out.write(line)
print('Import SQL generated at', import_path)
