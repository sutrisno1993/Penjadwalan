import re

with open(r'd:\Jadwal_BKS\frontend\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'd:\Jadwal_BKS\frontend\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("HTML page matches:", set(re.findall(r'id=["\'](pg-[\w-]+)["\']', html)))
print("JS page matches:", set(re.findall(r'["\'](pg-[\w-]+)["\']', js)))
