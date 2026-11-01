from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_openfeature import fleet_openfeature
def test_of():
    r = fleet_openfeature([{"active": True, "evaluations_24h": 100000}])
    assert r["evaluations_24h"] == 100000
    assert r["standard_adopted"]
