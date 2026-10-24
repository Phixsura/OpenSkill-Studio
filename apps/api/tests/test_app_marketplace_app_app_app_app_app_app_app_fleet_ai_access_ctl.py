from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_access_ctl import fleet_ai_access_control
def test_ac():
    r = fleet_ai_access_control([{"active": True, "policies": 200, "evaluations_24h": 50000000, "denied_24h": 1000}])
    assert r["policies"] == 200
    assert r["enforcing"]
