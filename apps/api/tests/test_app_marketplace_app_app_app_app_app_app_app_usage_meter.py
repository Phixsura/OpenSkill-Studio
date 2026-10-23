from app.services.app_marketplace_app_app_app_app_app_app_app_usage_meter import build_meter, build_meters

def test_meter():
    m = build_meter(label="API Calls", used=45000, limit=50000, unit="calls")
    assert m["pct"] == 90.0
    assert m["status"] == "critical"
    assert m["remaining"] == 5000

def test_meters():
    r = build_meters([
        {"label": "API Calls", "used": 45000, "limit": 50000},
        {"label": "Storage", "used": 2000, "limit": 10000, "unit": "MB"},
    ])
    assert r["total"] == 2
    assert r["critical_count"] == 1
    assert not r["all_ok"]
