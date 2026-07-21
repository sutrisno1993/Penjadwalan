import subprocess
import re

blobs = [
    ('96231eceebfaf5efbb237bd976eb95f09627db7e', 'index.html'),
    ('9208a51a481e8b290d73ee93918b2edaaad8c245', 'app.js'),
    ('62cbcbcadaacfb5459c73388ea81fac758674e64', 'main.py')
]

for blob, name in blobs:
    content = subprocess.check_output(['git', 'cat-file', '-p', blob]).decode('utf-8', errors='ignore')
    print(f"=== BLOB {blob[:8]} ({name}) length: {len(content)} lines: {len(content.splitlines())}")
    if name == 'index.html':
        btns = re.findall(r'data-page="([^"]+)"', content)
        print("Data-pages in blob index.html:", btns)

print("\n--- Checking current index.html ---")
with open(r'd:\Jadwal\frontend\index.html', 'r', encoding='utf-8') as f:
    curr_html = f.read()
btns_curr = re.findall(r'data-page="([^"]+)"', curr_html)
print("Data-pages in current index.html:", btns_curr)
