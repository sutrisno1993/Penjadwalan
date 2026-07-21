import urllib.request
import re

try:
    resp = urllib.request.urlopen('http://127.0.0.1:8002/')
    html = resp.read().decode('utf-8')
    btns = re.findall(r'data-page="([^"]+)"', html)
    print("HTTP 8002 returns pages:", btns)
    print(f"Total HTML length: {len(html)}")
except Exception as e:
    print("Error:", e)
