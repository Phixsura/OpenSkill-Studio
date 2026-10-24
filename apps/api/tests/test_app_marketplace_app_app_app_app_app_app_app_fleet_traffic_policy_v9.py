from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_traffic_policy_v9 import fleet_traffic_policy_v9
def test_tp2_v9():
    r = fleet_traffic_policy_v9([{"active": True, "type": "weighted"}])
    assert r["weighted"] == 1
    assert r["healthy"]
