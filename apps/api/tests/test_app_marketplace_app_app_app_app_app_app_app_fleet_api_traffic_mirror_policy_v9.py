from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_traffic_mirror_policy_v9 import fleet_api_traffic_mirror_policy_v9
def test_atmp_v9():
    r = fleet_api_traffic_mirror_policy_v9([{"active": True, "mirrored_rps": 5000, "discrepancies": 0}])
    assert r["mirrored_rps"] == 5000
    assert r["healthy"]
