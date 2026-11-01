from app.services.app_marketplace_app_app_app_app_app_app_app_rate_quota_dash import build_quota_dashboard

def test_dashboard():
    r = build_quota_dashboard([
        {"name": "API calls", "used": 450, "limit": 1000},
        {"name": "Storage", "used": 900, "limit": 1000},
        {"name": "Webhooks", "used": 50, "limit": 50},
    ])
    assert r["total"] == 3
    assert r["healthy"] == 1
    assert r["at_risk"] == 1
    assert r["exhausted"] == 1
    assert r["quotas"][0]["pct_used"] == 45.0
