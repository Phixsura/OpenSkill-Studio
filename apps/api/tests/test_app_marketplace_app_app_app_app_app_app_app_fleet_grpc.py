from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grpc import fleet_grpc_health
def test_grpc():
    r = fleet_grpc_health([{"status": "SERVING", "avg_latency_ms": 5}, {"status": "NOT_SERVING", "avg_latency_ms": 0}])
    assert r["serving"] == 1
    assert not r["healthy"]
