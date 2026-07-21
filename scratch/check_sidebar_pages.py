import re

with open(r'd:\Jadwal_BKS\frontend\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

nav_buttons = re.findall(r'data-page="(pg-[^"]+)"', text)
print("Data-page in sidebar buttons:", nav_buttons)

pages = re.findall(r'id="(pg-[^"]+)"', text)
print("Page containers in index.html:", pages)
