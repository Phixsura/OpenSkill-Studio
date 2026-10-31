from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_waf_v8 import fleet_ai_waf_v8
def test_wv8():
    r = fleet_ai_waf_v8([{"active": True, "rules": 5000, "blocked_24h": 5000000, "ml_rules": 500}])
    assert r["rules"] == 5000
    assert r["ai_powered"]
