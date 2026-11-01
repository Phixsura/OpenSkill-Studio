from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_edge_compute_v9 import fleet_edge_compute_v9
def test_edge_v9():
    r = fleet_edge_compute_v9([{"active": True, "latency_ms": 12, "region": "us-east"}, {"active": True, "latency_ms": 8, "region": "eu-west"}])
    assert r["total"] == 2
    assert r["regions"] == 2
    assert r["healthy"]
