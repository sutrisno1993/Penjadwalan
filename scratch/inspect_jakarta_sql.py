import re

with open(r'd:\Jadwal\jadwal_jakarta.sql', 'r', encoding='utf-8', errors='ignore') as f:
    sql_text = f.read()

tables_created = re.findall(r'CREATE TABLE [`"]?(\w+)[`"]?', sql_text, re.IGNORECASE)
tables_inserted = re.findall(r'INSERT INTO [`"]?(\w+)[`"]?', sql_text, re.IGNORECASE)

print("Tables in CREATE TABLE statements:", set(tables_created))
print("Tables in INSERT INTO statements:", set(tables_inserted))
