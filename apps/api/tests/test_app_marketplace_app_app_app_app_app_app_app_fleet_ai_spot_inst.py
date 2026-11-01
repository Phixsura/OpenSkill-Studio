from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_spot_inst import fleet_ai_spot_instance
def test_si():
    r = fleet_ai_spot_instance([{"active": True, "instances": 200, "savings_pct": 70, "interruptions": 5}])
    assert r["savings_pct"] == 70.0
    assert r["cost_effective"]
