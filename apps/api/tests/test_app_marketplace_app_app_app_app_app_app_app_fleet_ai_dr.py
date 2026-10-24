from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dr import fleet_ai_disaster_recovery
def test_dr():
    r = fleet_ai_disaster_recovery([{"active": True, "rto_min": 15, "rpo_min": 5, "last_drill_days": 7}])
    assert r["rto_min"] == 15
    assert r["prepared"]
