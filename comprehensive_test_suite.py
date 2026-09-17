import json
import urllib.request
import urllib.error
from pathlib import Path
import time
import os
import sys

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

class TestReporter:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []

    def assert_true(self, condition, test_name, details=""):
        self.total += 1
        if condition:
            self.passed += 1
            status_str = "[PASS]"
            self.results.append((test_name, "PASS", details))
            print(f" {status_str} {test_name}" + (f" -> {details}" if details else ""))
        else:
            self.failed += 1
            status_str = "[FAIL]"
            self.results.append((test_name, "FAIL", details))
            print(f" {status_str} {test_name}" + (f" -> {details}" if details else ""))

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SmartBio-Tester/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read(), resp.headers

def http_post_json(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "SmartBio-Tester/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def http_post_file(url, file_path, fields={}):
    boundary = f"----WebKitBoundary{int(time.time()*1000)}"
    body_parts = []
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    filename = Path(file_path).name
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode("utf-8"))
    body_parts.append(file_bytes)
    
    for k, v in fields.items():
        body_parts.append(f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
    
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    full_body = b"".join(body_parts)

    req = urllib.request.Request(url, data=full_body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def run_tests():
    reporter = TestReporter()
    print("================================================================================")
    print("   SMARTBIO FULL-STACK COMPREHENSIVE AUTOMATED VERIFICATION SUITE   ")
    print("================================================================================")

    # --------------------------------------------------------------------------
    # SECTION 1: Health & Calibration
    # --------------------------------------------------------------------------
    print("\n--- SECTION 1: System Health & Prototype Severity Calibration ---")
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/health")
        health = json.loads(content.decode("utf-8"))
        reporter.assert_true(status == 200 and health["status"] == "healthy", "Backend Health Check", f"Version: {health.get('version')}, Service: {health.get('service')}")
        reporter.assert_true("ai_model_available" in health, "AI Model Fallback Indicator Present", f"ai_model_available={health.get('ai_model_available')}")
    except Exception as e:
        reporter.assert_true(False, "Backend Health Check", str(e))

    try:
        status, content, _ = http_get(f"{BASE_URL}/api/thresholds")
        thresholds = json.loads(content.decode("utf-8"))
        reporter.assert_true(
            thresholds["LOW_MAX"] == 10.0 and thresholds["MEDIUM_MAX"] == 30.0 and thresholds["HIGH_MAX"] == 50.0,
            "Severity Thresholds Config",
            f"0-10% Low, 10-30% Med, 30-50% High, >50% Very High"
        )
        reporter.assert_true(len(thresholds.get("disclaimer", "")) > 20, "Academic Project Disclaimer Defined", thresholds["disclaimer"][:60] + "...")
    except Exception as e:
        reporter.assert_true(False, "Severity Thresholds Config", str(e))

    # --------------------------------------------------------------------------
    # SECTION 2: Security & Input Validation Tests (Negative / Edge Cases)
    # --------------------------------------------------------------------------
    print("\n--- SECTION 2: Security & Robustness Edge Case Validations ---")
    
    # 2.1 Test Unsupported File Upload (.txt file)
    txt_file = Path("backend/test_invalid.txt")
    with open(txt_file, "w") as f:
        f.write("This is not an image file.")
    try:
        status, data = http_post_file(f"{BASE_URL}/api/analyze", str(txt_file))
        reporter.assert_true(False, "Reject Unsupported File Extension (.txt)", "Expected client error, got 200")
    except urllib.error.HTTPError as e:
        reporter.assert_true(e.code in [400, 422], "Reject Unsupported File Extension (.txt)", f"HTTP {e.code} correctly returned for text upload")
    finally:
        if txt_file.exists():
            txt_file.unlink()

    # 2.2 Test Empty File Upload (0 bytes)
    empty_file = Path("backend/test_empty.jpg")
    with open(empty_file, "wb") as f:
        pass
    try:
        status, data = http_post_file(f"{BASE_URL}/api/analyze", str(empty_file))
        reporter.assert_true(False, "Reject Empty Image (0 bytes)", "Expected client error, got 200")
    except urllib.error.HTTPError as e:
        reporter.assert_true(e.code in [400, 422], "Reject Empty Image (0 bytes)", f"HTTP {e.code} correctly returned for 0-byte file")
    finally:
        if empty_file.exists():
            empty_file.unlink()

    # 2.3 Test Corrupted Image
    corrupt_file = Path("backend/test_corrupt.png")
    with open(corrupt_file, "wb") as f:
        f.write(b"PNG\r\n\x1a\n\x00\x00CORRUPTED_BINARY_DATA_NOT_A_VALID_IMAGE")
    try:
        status, data = http_post_file(f"{BASE_URL}/api/analyze", str(corrupt_file))
        reporter.assert_true(False, "Reject Corrupted Image File", "Expected client error, got 200")
    except urllib.error.HTTPError as e:
        reporter.assert_true(e.code in [400, 422], "Reject Corrupted Image File", f"HTTP {e.code} correctly caught by Pillow validator")
    finally:
        if corrupt_file.exists():
            corrupt_file.unlink()

    # --------------------------------------------------------------------------
    # SECTION 3: Fleet Vessel Management Lifecycle
    # --------------------------------------------------------------------------
    print("\n--- SECTION 3: Vessel Management & Fleet Registry ---")
    test_vessel_name = f"Test Vessel Alpha {int(time.time())}"
    vessel_id = None
    try:
        status, new_vessel = http_post_json(f"{BASE_URL}/api/vessels", {
            "vessel_name": test_vessel_name,
            "vessel_type": "Bulk Carrier",
            "notes": "Dedicated automated test vessel."
        })
        vessel_id = new_vessel["id"]
        reporter.assert_true(status == 201 and vessel_id is not None, "Create New Vessel", f"Created '{test_vessel_name}' with ID #{vessel_id}")
    except Exception as e:
        reporter.assert_true(False, "Create New Vessel", str(e))

    # Duplicate Vessel Name Rejection
    try:
        status, _ = http_post_json(f"{BASE_URL}/api/vessels", {
            "vessel_name": test_vessel_name,
            "vessel_type": "Bulk Carrier"
        })
        reporter.assert_true(False, "Reject Duplicate Vessel Name", "Expected 400 Bad Request, got 201")
    except urllib.error.HTTPError as e:
        reporter.assert_true(e.code == 400, "Reject Duplicate Vessel Name", f"HTTP {e.code} correctly caught duplicate name")

    # Get Single Vessel Detail
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/vessels/{vessel_id}")
        v_data = json.loads(content.decode("utf-8"))
        reporter.assert_true(v_data["vessel_name"] == test_vessel_name, "Retrieve Vessel by ID", f"ID #{vessel_id} retrieved with type {v_data['vessel_type']}")
    except Exception as e:
        reporter.assert_true(False, "Retrieve Vessel by ID", str(e))

    # --------------------------------------------------------------------------
    # SECTION 4: Image Ingestion & OpenCV Computer Vision Analysis
    # --------------------------------------------------------------------------
    print("\n--- SECTION 4: OpenCV Computer-Vision Biofouling Analysis ---")
    sample_images = list(Path("backend/uploads").glob("*.jpg"))
    reporter.assert_true(len(sample_images) > 0, "Sample Hull Images Available", f"Found {len(sample_images)} test images")
    test_img = str(sample_images[0])

    analysis_res1 = None
    try:
        status, analysis_res1 = http_post_file(f"{BASE_URL}/api/analyze", test_img, {"vessel_id": str(vessel_id), "mode": "DEMO"})
        cov = analysis_res1["coverage_percentage"]
        reporter.assert_true(0.0 <= cov <= 100.0, "Coverage Percentage Range (0-100%)", f"Estimated Coverage: {cov:.2f}%")
        reporter.assert_true(analysis_res1["severity"] in ["LOW", "MEDIUM", "HIGH", "VERY HIGH"], "Severity Classification Validity", f"Severity: {analysis_res1['severity']}")
        reporter.assert_true(analysis_res1["analysis_mode"] == "DEMO", "Analysis Mode Labeled as DEMO", analysis_res1["confidence"])
        reporter.assert_true(analysis_res1["analyzable_pixels"] > 0 and analysis_res1["fouling_pixels"] >= 0, "Pixel Counts Computed", f"Analyzable: {analysis_res1['analyzable_pixels']:,} px | Fouling: {analysis_res1['fouling_pixels']:,} px")
        
        # Verify generated processed overlay and mask files exist on disk
        proc_disk_path = Path("backend") / analysis_res1["processed_image_path"].lstrip("/")
        mask_disk_path = Path("backend") / analysis_res1["mask_image_path"].lstrip("/")
        reporter.assert_true(proc_disk_path.exists(), "Processed Overlay File Saved on Disk", str(proc_disk_path.name))
        reporter.assert_true(mask_disk_path.exists(), "Binary Mask File Saved on Disk", str(mask_disk_path.name))
    except Exception as e:
        reporter.assert_true(False, "OpenCV Biofouling Analysis", str(e))

    # --------------------------------------------------------------------------
    # SECTION 5: Save Inspections & Temporal Growth Rate Mathematics
    # --------------------------------------------------------------------------
    print("\n--- SECTION 5: Sequential Inspection Storage & Growth Mathematics ---")
    # Save Inspection 1 (Baseline: e.g. 10.0%)
    insp1_id = None
    try:
        status, insp1 = http_post_json(f"{BASE_URL}/api/inspections", {
            "vessel_id": vessel_id,
            "original_image_path": analysis_res1["original_image_path"],
            "processed_image_path": analysis_res1["processed_image_path"],
            "mask_image_path": analysis_res1["mask_image_path"],
            "coverage_percentage": 10.0,
            "severity": "LOW",
            "analysis_mode": "DEMO",
            "recommendation": "Baseline inspection: Continue routine monitoring.",
            "notes": "Baseline Hull Audit #1"
        })
        insp1_id = insp1["id"]
        reporter.assert_true(insp1_id is not None, "Save Baseline Inspection #1", f"ID #{insp1_id}, Coverage: 10.0%, Prev Coverage: {insp1.get('previous_coverage')}")
    except Exception as e:
        reporter.assert_true(False, "Save Baseline Inspection #1", str(e))

    # Save Inspection 2 (Subsequent growth: e.g. 24.5%)
    # Expected Absolute Growth: 24.5 - 10.0 = +14.5 pp
    # Expected Relative Growth: ((24.5 - 10.0) / 10.0) * 100 = +145.0%
    insp2_id = None
    try:
        status, insp2 = http_post_json(f"{BASE_URL}/api/inspections", {
            "vessel_id": vessel_id,
            "original_image_path": analysis_res1["original_image_path"],
            "processed_image_path": analysis_res1["processed_image_path"],
            "mask_image_path": analysis_res1["mask_image_path"],
            "coverage_percentage": 24.5,
            "severity": "MEDIUM",
            "analysis_mode": "DEMO",
            "notes": "Follow-up Hull Audit #2 after 14 days"
        })
        insp2_id = insp2["id"]
        abs_growth = insp2.get("absolute_growth_pp")
        rel_growth = insp2.get("relative_growth_pct")

        reporter.assert_true(abs(abs_growth - 14.5) < 0.01, "Absolute Growth Calculation (Current - Previous)", f"Expected +14.5 pp, got {abs_growth} pp")
        reporter.assert_true(abs(rel_growth - 145.0) < 0.01, "Relative Growth Calculation (((Curr-Prev)/Prev)*100)", f"Expected +145.0%, got {rel_growth}%")
        reporter.assert_true("Rapid growth detected" in insp2.get("recommendation", ""), "Rapid Growth Triggered (Delta >= 5.0 pp)", insp2.get("recommendation")[:70] + "...")
    except Exception as e:
        reporter.assert_true(False, "Save Inspection #2 with Growth Verification", str(e))

    # --------------------------------------------------------------------------
    # SECTION 6: Side-by-Side Comparison Differential Analysis
    # --------------------------------------------------------------------------
    print("\n--- SECTION 6: Side-by-Side Differential Comparison ---")
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/compare?previous_id={insp1_id}&current_id={insp2_id}")
        comp = json.loads(content.decode("utf-8"))
        reporter.assert_true(status == 200, "Comparison Endpoint Status 200", f"Summary: {comp['summary']}")
        reporter.assert_true(comp["severity_changed"] is True, "Severity Transition Flagged (LOW -> MEDIUM)", f"Previous: {comp['previous']['severity']} | Current: {comp['current']['severity']}")
        reporter.assert_true(comp["cleaning_review_required"] is True, "Cleaning Review Required Flagged", f"Cleaning required = {comp['cleaning_review_required']}")
    except Exception as e:
        reporter.assert_true(False, "Differential Comparison Analysis", str(e))

    # --------------------------------------------------------------------------
    # SECTION 7: Academic Inspection Report Generation
    # --------------------------------------------------------------------------
    print("\n--- SECTION 7: Official Inspection Audit Report ---")
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/report/{insp2_id}")
        rep = json.loads(content.decode("utf-8"))
        reporter.assert_true(status == 200 and rep["report_id"].startswith("SB-REP-"), "Generate Formal Report ID", rep["report_id"])
        reporter.assert_true(rep["vessel_name"] == test_vessel_name, "Report Maps Correct Vessel Name", rep["vessel_name"])
        reporter.assert_true("prototype software estimate" in rep["disclaimer"].lower(), "Mandatory Academic Disclaimer Included", rep["disclaimer"][:65] + "...")
    except Exception as e:
        reporter.assert_true(False, "Generate Official Inspection Report", str(e))

    # --------------------------------------------------------------------------
    # SECTION 8: Time-Series Recharts Growth Feed
    # --------------------------------------------------------------------------
    print("\n--- SECTION 8: Time-Series Recharts Data Delivery ---")
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/vessels/{vessel_id}/growth")
        growth = json.loads(content.decode("utf-8"))
        reporter.assert_true(growth["total_inspections"] == 2, "Accurate Total Inspection Count in Growth Feed", f"Total: {growth['total_inspections']}")
        reporter.assert_true(len(growth["data_points"]) == 2, "Data Points Array for Recharts AreaChart", f"Points count: {len(growth['data_points'])}")
        reporter.assert_true(growth["latest_coverage"] == 24.5, "Latest Coverage in Growth Feed", f"{growth['latest_coverage']}%")
    except Exception as e:
        reporter.assert_true(False, "Time-Series Growth Feed", str(e))

    # --------------------------------------------------------------------------
    # SECTION 9: Inspection Querying & Filters
    # --------------------------------------------------------------------------
    print("\n--- SECTION 9: Audit Log Querying & Filtering ---")
    try:
        status, content, _ = http_get(f"{BASE_URL}/api/inspections?vessel_id={vessel_id}")
        v_inspections = json.loads(content.decode("utf-8"))
        reporter.assert_true(len(v_inspections) == 2, "Filter Inspections by Vessel ID", f"Found {len(v_inspections)} audits for vessel #{vessel_id}")

        status, content, _ = http_get(f"{BASE_URL}/api/inspections?severity=LOW")
        low_inspections = json.loads(content.decode("utf-8"))
        reporter.assert_true(all(i["severity"] == "LOW" for i in low_inspections), "Filter Inspections by Severity (LOW)", f"Retrieved {len(low_inspections)} LOW audits")
    except Exception as e:
        reporter.assert_true(False, "Audit Log Querying & Filtering", str(e))

    # --------------------------------------------------------------------------
    # SECTION 10: Deletion & Safe File Cleanup
    # --------------------------------------------------------------------------
    print("\n--- SECTION 10: Safe Deletion & Storage Cleanup ---")
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/inspections/{insp2_id}", method="DELETE")
        with urllib.request.urlopen(req) as resp:
            reporter.assert_true(resp.status == 200, "Delete Inspection by ID", f"Deleted audit #{insp2_id}")

        # Verify 404 after deletion
        try:
            http_get(f"{BASE_URL}/api/inspections/{insp2_id}")
            reporter.assert_true(False, "Audit Removed from Database", "Expected 404 Not Found")
        except urllib.error.HTTPError as e:
            reporter.assert_true(e.code == 404, "Audit Removed from Database", f"Confirmed HTTP 404 Not Found for deleted ID #{insp2_id}")
    except Exception as e:
        reporter.assert_true(False, "Delete Inspection by ID", str(e))

    # --------------------------------------------------------------------------
    # SECTION 11: Single-Page Application (SPA) Serving & Static Assets
    # --------------------------------------------------------------------------
    print("\n--- SECTION 11: Frontend Serving, Assets & Proxy Integrity ---")
    # Test FastAPI port 8000 SPA serving
    try:
        status, html_bytes, _ = http_get(f"{BASE_URL}/")
        html_str = html_bytes.decode("utf-8")
        reporter.assert_true(status == 200 and "<div id=\"root\"></div>" in html_str, "FastAPI Port 8000 Serves Built React SPA", f"HTML size: {len(html_bytes):,} bytes")
    except Exception as e:
        reporter.assert_true(False, "FastAPI Port 8000 Serves Built React SPA", str(e))

    # Test client-side routing fallback on port 8000
    try:
        status, html_bytes, _ = http_get(f"{BASE_URL}/dashboard")
        html_str = html_bytes.decode("utf-8")
        reporter.assert_true(status == 200 and "<div id=\"root\"></div>" in html_str, "Client-Side Route Fallback (/dashboard)", "FastAPI correctly serves SPA index.html for client routes")
    except Exception as e:
        reporter.assert_true(False, "Client-Side Route Fallback (/dashboard)", str(e))

    # Test Vite Port 5173 Dev Server
    try:
        status, html_bytes, _ = http_get(f"{FRONTEND_URL}/")
        reporter.assert_true(status == 200, "Vite Port 5173 Dev Server Operational", f"Returned HTTP {status}")
    except Exception as e:
        reporter.assert_true(False, "Vite Port 5173 Dev Server Operational", str(e))

    # Test Vite Dev Proxy to /api/health
    try:
        status, json_bytes, _ = http_get(f"{FRONTEND_URL}/api/health")
        p_health = json.loads(json_bytes.decode("utf-8"))
        reporter.assert_true(status == 200 and p_health["status"] == "healthy", "Vite Dev Proxy to Backend (/api/health)", "Proxy forwarding 100% operational")
    except Exception as e:
        reporter.assert_true(False, "Vite Dev Proxy to Backend (/api/health)", str(e))

    # --------------------------------------------------------------------------
    # SUMMARY REPORT
    # --------------------------------------------------------------------------
    print("\n================================================================================")
    print(f"   TEST SUMMARY: {reporter.passed}/{reporter.total} PASSED ({reporter.failed} FAILED) - Success Rate: {(reporter.passed/reporter.total)*100:.1f}%")
    print("================================================================================")
    
    return reporter.failed == 0

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
