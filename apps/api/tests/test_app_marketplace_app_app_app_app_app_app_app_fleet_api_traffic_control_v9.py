from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_traffic_control_v9 import fleet_api_traffic_control_v9
def test_atc2_v9():
    r = fleet_api_traffic_control_v9([{"active": True, "rps": 100000, "policies": 20}])
    assert r["rps_managed"] == 100000
    assert r["healthy"]
