from app.services.app_marketplace_app_app_app_app_app_app_app_img_scanner import scan_image, registry_scan

def test_scan():
    r = scan_image("api", "v3.0", 12, 250, [
        {"cve": "CVE-1", "severity": "medium"}, {"cve": "CVE-2", "severity": "low"}])
    assert r["pass"]
    assert r["vulns"] == 2
    assert r["critical"] == 0

def test_fail():
    r = scan_image("old", "v1", 25, 800, [{"cve": "CVE-3", "severity": "critical"}])
    assert not r["pass"]
    assert len(r["issues"]) == 2  # too large + too many layers

def test_registry():
    images = [{"pass": True, "vulns": 2}, {"pass": False, "vulns": 5}]
    r = registry_scan(images)
    assert r["pass_rate"] == 50
    assert r["total_vulns"] == 7
