from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_grpc_gateway_v9 import fleet_api_grpc_gateway_v9
def test_agrpcgw_v9():
    r = fleet_api_grpc_gateway_v9([{"active": True, "requests_today": 100000, "methods": 50}])
    assert r["transcoded_today"] == 100000
    assert r["healthy"]
