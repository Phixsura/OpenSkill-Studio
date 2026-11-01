from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_early_stop import fleet_ai_early_stopping
def test_es():
    r = fleet_ai_early_stopping([{"active": True, "jobs": 100, "stopped": 30, "saved_pct": 25}])
    assert r["stopped"] == 30
    assert r["efficient"]
