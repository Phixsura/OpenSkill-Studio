from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grpc_proxy_v9 import fleet_grpc_proxy_v9
def test_grpc_v9():
    r = fleet_grpc_proxy_v9([{"active": True, "rps": 20000, "errors": 0}])
    assert r["total_rps"] == 20000
    assert r["healthy"]
