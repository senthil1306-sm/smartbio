import urllib.request
import urllib.parse
import json
import sys
from pathlib import Path

def test_e2e():
    print("==================================================")
    print(" SmartBio End-to-End System & API Verification ")
    print("==================================================")

    # 1. Backend direct health
    print("\n1. Testing Backend Health (http://127.0.0.1:8000/api/health)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        print("   [OK] Backend is healthy:", data)

    # 2. Frontend HTTP serving
    print("\n2. Testing Frontend Dev Server (http://127.0.0.1:5173/)...")
    req = urllib.request.Request("http://127.0.0.1:5173/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        html = resp.read().decode('utf-8')
        assert "<div id=\"root\"></div>" in html
        assert "SmartBio" in html
        print("   [OK] Frontend index.html served successfully (Length:", len(html), "bytes)")

    # 3. Vite Proxy to Backend
    print("\n3. Testing Vite Dev Proxy (http://127.0.0.1:5173/api/health)...")
    req = urllib.request.Request("http://127.0.0.1:5173/api/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        proxy_data = json.loads(resp.read().decode('utf-8'))
        print("   [OK] Vite proxy works cleanly:", proxy_data["service"])

    # 4. Vessels Query
    print("\n4. Testing GET /api/vessels...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/vessels")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        vessels = json.loads(resp.read().decode('utf-8'))
        print(f"   [OK] Found {len(vessels)} vessel(s):")
        for v in vessels:
            print(f"        • ID {v['id']}: {v['vessel_name']} ({v['vessel_type']}) - {v['inspection_count']} inspections")
        vessel_id = vessels[0]["id"]

    # 5. Vessel Growth Time-Series
    print(f"\n5. Testing GET /api/vessels/{vessel_id}/growth...")
    req = urllib.request.Request(f"http://127.0.0.1:8000/api/vessels/{vessel_id}/growth")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        growth = json.loads(resp.read().decode('utf-8'))
        print(f"   [OK] Total timeline audits: {growth['total_inspections']}, Latest Coverage: {growth['latest_coverage']}%, Status: {growth['cleaning_status']}")
        for dp in growth["data_points"]:
            print(f"        {dp['inspection_date']}: {dp['coverage_percentage']}% ({dp['severity']}) - Abs: {dp['absolute_growth_pp']} pp, Rel: {dp['relative_growth_pct']}%")

    # 6. Compare Two Inspections
    print("\n6. Testing GET /api/compare?previous_id=1&current_id=5...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/compare?previous_id=1&current_id=5")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        comp = json.loads(resp.read().decode('utf-8'))
        print("   [OK] Comparison Result:")
        print("        Summary:", comp["summary"])
        print("        Delta:", comp["absolute_growth_pp"], "pp | Cleaning required:", comp["cleaning_review_required"])

    # 7. Generate Inspection Report
    print("\n7. Testing GET /api/report/5...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/report/5")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        rep = json.loads(resp.read().decode('utf-8'))
        print(f"   [OK] Report ID: {rep['report_id']}")
        print(f"        Recommendation: {rep['recommendation']}")
        print(f"        Disclaimer verified: '{rep['disclaimer'][:65]}...'")

    # 8. Media Static Asset Serving through Proxy
    print("\n8. Testing Image Asset Serving (http://127.0.0.1:5173" + rep['processed_image_path'] + ")...")
    req = urllib.request.Request("http://127.0.0.1:5173" + rep['processed_image_path'])
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        img_bytes = resp.read()
        print(f"   [OK] Image served successfully ({len(img_bytes)} bytes, Content-Type: {resp.headers.get('Content-Type')})")

    print("\n==================================================")
    print(" ALL 8 TESTS PASSED SUCCESSFULLY! ")
    print(" Full-stack web application is fully operational. ")
    print("==================================================")

if __name__ == "__main__":
    test_e2e()
