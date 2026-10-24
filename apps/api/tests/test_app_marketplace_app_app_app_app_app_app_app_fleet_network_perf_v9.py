from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_perf_v9 import fleet_network_perf_v9
def test_np_v9():
    r = fleet_network_perf_v9([{"packet_loss": 0, "latency_ms": 5, "bandwidth_gbps": 100}])
    assert r["avg_latency_ms"] == 5.0
    assert r["healthy"]
