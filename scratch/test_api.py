import urllib.request
try:
    req = urllib.request.Request('http://127.0.0.1:8001/api/settings')
    urllib.request.urlopen(req)
except Exception as e:
    if hasattr(e, 'read'):
        print(e.read().decode())
    else:
        print(e)
