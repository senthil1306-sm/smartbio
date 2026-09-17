import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system():
    print("Testing GET /api/health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[PASS] Health check:", r.json())

    print("\nTesting GET /api/vessels...")
    r = client.get("/api/vessels")
    assert r.status_code == 200, f"Get vessels failed: {r.text}"
    vessels = r.json()
    print(f"[PASS] Found {len(vessels)} vessels: {[v['vessel_name'] for v in vessels]}")
    vessel_id = vessels[0]["id"]

    print(f"\nTesting GET /api/vessels/{vessel_id}/growth...")
    r = client.get(f"/api/vessels/{vessel_id}/growth")
    assert r.status_code == 200, f"Growth query failed: {r.text}"
    growth = r.json()
    print(f"[PASS] Growth data points: {len(growth['data_points'])}, cleaning status: {growth['cleaning_status']}")
    for dp in growth["data_points"]:
        print(f"   Date: {dp['inspection_date']} | Cov: {dp['coverage_percentage']}% | Abs: {dp['absolute_growth_pp']} pp | Rel: {dp['relative_growth_pct']}%")

    print("\nTesting GET /api/inspections...")
    r = client.get("/api/inspections")
    assert r.status_code == 200
    inspections = r.json()
    print(f"[PASS] Retrieved {len(inspections)} inspections")
    assert len(inspections) >= 2

    id1 = inspections[-1]["id"]
    id2 = inspections[0]["id"]
    print(f"\nTesting GET /api/compare?previous_id={id1}&current_id={id2}...")
    r = client.get(f"/api/compare?previous_id={id1}&current_id={id2}")
    assert r.status_code == 200, f"Compare failed: {r.text}"
    comp = r.json()
    print("[PASS] Compare summary:", comp["summary"])
    print(f"   Absolute growth: {comp['absolute_growth_pp']} pp | Relative: {comp['relative_growth_pct']}% | Alert required: {comp['cleaning_review_required']}")

    print(f"\nTesting GET /api/report/{id2}...")
    r = client.get(f"/api/report/{id2}")
    assert r.status_code == 200, f"Report failed: {r.text}"
    rep = r.json()
    print(f"[PASS] Generated Report ID: {rep['report_id']} for vessel '{rep['vessel_name']}'")

    print("\nTesting POST /api/analyze with sample image...")
    sample_imgs = list((backend_dir / "uploads").glob("*.jpg"))
    assert len(sample_imgs) > 0, "No sample images found"
    with open(sample_imgs[0], "rb") as f:
        files = {"file": ("test_hull.jpg", f, "image/jpeg")}
        data = {"vessel_id": str(vessel_id), "mode": "DEMO"}
        r = client.post("/api/analyze", files=files, data=data)
    assert r.status_code == 200, f"Analyze failed: {r.text}"
    analysis = r.json()
    print(f"[PASS] Analyze successful: Coverage = {analysis['coverage_percentage']}%, Severity = {analysis['severity']}, Mode = {analysis['analysis_mode']}")
    print(f"   Recommendation: {analysis['recommendation']}")

    print("\nAll Backend Tests PASSED!")

if __name__ == "__main__":
    test_system()
