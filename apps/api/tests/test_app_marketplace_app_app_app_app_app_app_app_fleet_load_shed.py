from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_load_shed import fleet_load_shedding
def test_shed():
    r = fleet_load_shedding([{"shedding_active": True, "requests_shed": 500}, {"shedding_active": False}])
    assert r["shedding"] == 1
    assert r["requests_shed"] == 500
    assert not r["calm"]
