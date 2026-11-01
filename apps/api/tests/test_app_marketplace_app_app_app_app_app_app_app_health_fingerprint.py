from app.services.app_marketplace_app_app_app_app_app_app_app_health_fingerprint import create_fingerprint, compare_fingerprints

def test_fingerprint():
    fp = create_fingerprint("api", {"uptime_pct": 99.99, "error_rate": 0.1, "p99_ms": 100})
    assert fp["level"] == "green"
    assert len(fp["fingerprint"]) == 16

def test_compare():
    fp1 = create_fingerprint("api", {"uptime_pct": 99.99, "error_rate": 0.1, "p99_ms": 100})
    fp2 = create_fingerprint("api", {"uptime_pct": 95, "error_rate": 10, "p99_ms": 2000})
    r = compare_fingerprints(fp1, fp2)
    assert r["level_changed"]
    assert r["from_level"] == "green"
    assert r["to_level"] == "red"
