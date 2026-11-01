from app.services.app_marketplace_app_app_app_app_app_app_app_secret_leak import scan_for_secrets, scan_summary

def test_detect():
    r = scan_for_secrets('API_KEY = "sk_live_abc123def456ghi"', "config.py")
    assert r["finding_count"] >= 1
    assert not r["clean"]

def test_clean():
    r = scan_for_secrets("const x = 42;", "app.js")
    assert r["clean"]
    assert r["finding_count"] == 0

def test_summary():
    results = [{"finding_count": 2, "clean": False}, {"finding_count": 0, "clean": True}]
    r = scan_summary(results)
    assert r["total_findings"] == 2
    assert r["clean_files"] == 1
    assert not r["pass"]
