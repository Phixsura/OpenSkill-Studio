from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_traffic_mirror_v9 import fleet_traffic_mirror_v9
def test_tm2_v9():
    r = fleet_traffic_mirror_v9([{"active": True, "rps": 5000, "discrepancies": 0}])
    assert r["rps_mirrored"] == 5000
    assert r["healthy"]
