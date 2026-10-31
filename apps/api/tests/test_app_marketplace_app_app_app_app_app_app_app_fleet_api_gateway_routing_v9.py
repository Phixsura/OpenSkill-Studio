from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_gateway_routing_v9 import fleet_api_gateway_routing_v9
def test_agr2_v9():
    r = fleet_api_gateway_routing_v9([{"active": True, "type": "path", "rps": 50000}])
    assert r["path_based"] == 1
    assert r["healthy"]
