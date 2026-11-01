from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_request_routing_v9 import fleet_request_routing_v9
def test_rr2_v9():
    r = fleet_request_routing_v9([{"active": True, "weighted_routes": 5, "header_routes": 3}])
    assert r["weighted_routes"] == 5
    assert r["healthy"]
