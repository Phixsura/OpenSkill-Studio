from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_waf_v4 import fleet_ai_waf_v4
def test_wv4():
    r = fleet_ai_waf_v4([{"active": True, "rules": 1000, "blocked": 500000, "ml_rules": 200}])
    assert r["ml_rules"] == 200
    assert r["ai_powered"]
