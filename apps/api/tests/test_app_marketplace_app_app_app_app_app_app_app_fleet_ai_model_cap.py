from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_cap import fleet_ai_model_capacity
def test_mc():
    r = fleet_ai_model_capacity([{"active": True, "models": 100, "max_rps": 500000, "util_pct": 65}])
    assert r["max_rps"] == 500000
    assert r["headroom"]
