import subprocess

# Lost blobs found via git fsck
blob_index_html = "96231eceebfaf5efbb237bd976eb95f09627db7e"
blob_app_js     = "9208a51a481e8b290d73ee93918b2edaaad8c245"
blob_main_py    = "62cbcbcadaacfb5459c73388ea81fac758674e64"

print("Restoring frontend/index.html from blob", blob_index_html[:8])
html_content = subprocess.check_output(['git', 'cat-file', '-p', blob_index_html]).decode('utf-8')
with open(r'd:\Jadwal_BKS\frontend\index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Restoring frontend/app.js from blob", blob_app_js[:8])
app_content = subprocess.check_output(['git', 'cat-file', '-p', blob_app_js]).decode('utf-8')
with open(r'd:\Jadwal_BKS\frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Restoring backend/main.py from blob", blob_main_py[:8])
main_content = subprocess.check_output(['git', 'cat-file', '-p', blob_main_py]).decode('utf-8')
with open(r'd:\Jadwal_BKS\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("=== ALL LOST FEATURES SUCCESSFULLY RESTORED ===")
