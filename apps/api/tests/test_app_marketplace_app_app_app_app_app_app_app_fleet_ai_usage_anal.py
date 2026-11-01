from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_usage_anal import fleet_ai_usage_analytics
def test_ua():
    r = fleet_ai_usage_analytics([{"active": True, "dau": 100000, "requests_24h": 50000000, "retention_pct": 85}])
    assert r["dau"] == 100000
    assert r["growing"]
