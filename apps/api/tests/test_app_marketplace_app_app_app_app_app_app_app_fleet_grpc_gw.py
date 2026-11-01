from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grpc_gw import fleet_grpc_gateway
def test_gg():
    r = fleet_grpc_gateway([{"active": True, "rps": 5000, "transcoded_24h": 1000000}])
    assert r["transcoded_24h"] == 1000000
    assert r["all_active"]
