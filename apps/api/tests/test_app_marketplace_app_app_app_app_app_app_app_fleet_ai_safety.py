from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_safety import fleet_ai_safety
def test_safety():
    r = fleet_ai_safety([{"active": True, "violations_24h": 0, "checks_24h": 1000000}])
    assert r["checks_24h"] == 1000000
    assert r["safe"]
