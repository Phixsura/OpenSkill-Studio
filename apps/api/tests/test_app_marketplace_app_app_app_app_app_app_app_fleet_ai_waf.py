from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_waf import fleet_ai_waf
def test_waf():
    r = fleet_ai_waf([{"active": True, "requests_24h": 100000000, "blocked_24h": 50000, "rules": 200}])
    assert r["rules"] == 200
    assert r["protecting"]
