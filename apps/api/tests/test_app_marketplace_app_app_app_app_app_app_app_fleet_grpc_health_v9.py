from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grpc_health_v9 import fleet_grpc_health_v9
def test_grpch_v9():
    r = fleet_grpc_health_v9([{"status": "SERVING", "active_streams": 100}])
    assert r["serving"] == 1
    assert r["healthy"]
