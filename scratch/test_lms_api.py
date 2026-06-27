import urllib.request
import json
import urllib.error

req = urllib.request.Request(
    'http://localhost:8000/api/v1/sync-all',
    data=json.dumps({}).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer token_rahasia_sitab_11maret'},
    method='POST'
)
try:
    with urllib.request.urlopen(req) as f:
        print(f.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(e)
