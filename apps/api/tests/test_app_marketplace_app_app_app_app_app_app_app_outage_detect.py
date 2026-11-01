from app.services.app_marketplace_app_app_app_app_app_app_app_outage_detect import detect_outage, outage_impact

def test_no_outage():
    r = detect_outage([
        {"name": "api", "status": "up"},
        {"name": "db", "status": "up"},
    ])
    assert not r["outage"]

def test_partial():
    r = detect_outage([
        {"name": "api", "status": "up"},
        {"name": "db", "status": "down"},
        {"name": "cache", "status": "up"},
    ])
    assert r["outage"]
    assert r["classification"] == "partial"
    assert r["down_count"] == 1

def test_major():
    r = detect_outage([
        {"name": "api", "status": "down"},
        {"name": "db", "status": "down"},
        {"name": "cache", "status": "up"},
    ])
    assert r["classification"] == "major"

def test_impact():
    outage = {"classification": "major", "affected": 3}
    r = outage_impact(outage, 10000)
    assert r["severity"] == "critical"
