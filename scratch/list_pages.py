import re

with open(r'd:\Jadwal_BKS\frontend\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pages = re.findall(r'id="(pg-[^"]+)"', text)
print("Page IDs in index.html:", pages)
