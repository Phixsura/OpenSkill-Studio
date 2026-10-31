from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_opt_state import fleet_ai_optimizer_state
def test_os():
    r = fleet_ai_optimizer_state([{"active": True, "states": 5000, "storage_gb": 500, "restorations": 200}])
    assert r["states"] == 5000
    assert r["persistent"]
