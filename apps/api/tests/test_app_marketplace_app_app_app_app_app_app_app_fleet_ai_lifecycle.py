from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lifecycle import fleet_ai_lifecycle
def test_lc():
    r = fleet_ai_lifecycle([{"active": True, "models": 100, "dev": 20, "staging": 10, "production": 60, "retired": 10}])
    assert r["models"] == 100
    assert r["managed"]
