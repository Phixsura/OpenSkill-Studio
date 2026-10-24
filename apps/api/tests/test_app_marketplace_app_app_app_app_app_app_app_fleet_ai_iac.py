from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_iac import fleet_ai_iac
def test_iac():
    r = fleet_ai_iac([{"active": True, "resources": 5000, "applies_24h": 50, "drift_free_pct": 99}])
    assert r["resources"] == 5000
    assert r["automated"]
