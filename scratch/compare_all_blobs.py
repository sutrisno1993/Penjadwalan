import subprocess
import os

dangling_blobs = [
    '9208a51a481e8b290d73ee93918b2edaaad8c245',
    'c31a6ab5e3c5290f321f48d68d551e54f93c9fac',
    '6117a361f1a6957994d0d135b742ca1ec7956377',
    '62cbcbcadaacfb5459c73388ea81fac758674e64',
    '96231eceebfaf5efbb237bd976eb95f09627db7e',
    'f30bc1f1fa04632e05c81d239bf45cb554db8983'
]

for blob in dangling_blobs:
    try:
        content = subprocess.check_output(['git', 'cat-file', '-p', blob]).decode('utf-8', errors='ignore')
        lines = content.splitlines()
        print(f"Blob {blob[:8]}: {len(content)} bytes, {len(lines)} lines | Header: {lines[0] if lines else 'empty'}")
    except Exception as e:
        print(f"Error reading blob {blob}: {e}")

print("\n--- Current Workspace Files ---")
for path in ['frontend/index.html', 'frontend/app.js', 'backend/main.py', 'backend/database.py']:
    full = os.path.join(r'd:\Jadwal', path)
    if os.path.exists(full):
        with open(full, 'r', encoding='utf-8', errors='ignore') as f:
            c = f.read()
            print(f"Current {path}: {len(c)} bytes, {len(c.splitlines())} lines")
