from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_loc import fleet_data_locality
def test_loc():
    r = fleet_data_locality([{"region_compliant": True}, {"region_compliant": False}])
    assert r["violations"] == 1
    assert not r["fully_compliant"]
