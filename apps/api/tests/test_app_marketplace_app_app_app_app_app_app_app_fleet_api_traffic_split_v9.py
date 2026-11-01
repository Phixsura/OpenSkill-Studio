from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_traffic_split_v9 import fleet_api_traffic_split_v9
def test_ats2_v9():
    r = fleet_api_traffic_split_v9([{"active": True, "canary_pct": 10, "rps": 50000}])
    assert r["avg_canary_pct"] == 10.0
    assert r["healthy"]
