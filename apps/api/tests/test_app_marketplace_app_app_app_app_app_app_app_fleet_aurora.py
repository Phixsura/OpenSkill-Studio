from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_aurora import fleet_aurora_status
def test_aurora():
    r = fleet_aurora_status([{"status": "available", "serverless": True, "current_acu": 8}])
    assert r["serverless"] == 1
    assert r["current_acu"] == 8
    assert r["all_available"]
