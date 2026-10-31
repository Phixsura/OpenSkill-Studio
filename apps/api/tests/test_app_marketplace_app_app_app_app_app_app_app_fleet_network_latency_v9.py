from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_latency_v9 import fleet_network_latency_v9
def test_nl2_v9():
    r = fleet_network_latency_v9([{"latency_ms": 5, "sla_ms": 50, "p99_ms": 20}])
    assert r["within_sla"] == 1
    assert r["healthy"]
