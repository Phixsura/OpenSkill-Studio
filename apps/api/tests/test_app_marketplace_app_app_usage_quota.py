from app.services.app_marketplace_app_app_usage_quota import build_usage_quota

def test_quota():
    resources = [
        {"name": "API Calls", "used": 8500, "limit": 10000, "unit": "calls/mo"},
        {"name": "Storage", "used": 2, "limit": 10, "unit": "GB"},
        {"name": "Bandwidth", "used": 95, "limit": 100, "unit": "GB"},
    ]
    r = build_usage_quota(resources=resources)
    assert r["total"] == 3
    assert r["has_warnings"]
    assert len(r["warnings"]) == 2  # API Calls 85% + Bandwidth 95%
    assert r["resources"][2]["status"] == "critical"
    assert r["resources"][1]["status"] == "ok"

def test_zero_limit():
    r = build_usage_quota(resources=[{"name": "X", "used": 5, "limit": 0}])
    assert r["resources"][0]["pct"] == 0
