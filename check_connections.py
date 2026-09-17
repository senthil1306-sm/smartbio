import urllib.request
import json

urls_to_test = [
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000/api/health",
    "http://127.0.0.1:8000/dashboard",
    "http://127.0.0.1:5173/",
    "http://localhost:8000/",
    "http://localhost:5173/"
]

for url in urls_to_test:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            print(f"[SUCCESS] {url} -> Status {resp.status} (Length: {len(content)} bytes)")
    except Exception as e:
        print(f"[FAIL] {url} -> {e}")
