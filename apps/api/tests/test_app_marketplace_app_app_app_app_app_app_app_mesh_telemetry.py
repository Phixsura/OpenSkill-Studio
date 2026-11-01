from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_telemetry import aggregate_mesh_traffic

def test_aggregate():
    r = aggregate_mesh_traffic([
        {"source": "api", "destination": "db", "requests": 100, "errors": 2, "latency_ms": 500},
        {"source": "api", "destination": "cache", "requests": 200, "errors": 0, "latency_ms": 100},
        {"source": "web", "destination": "api", "requests": 150, "errors": 5, "latency_ms": 750},
    ])
    assert r["unique_pairs"] == 3
    assert r["total_requests"] == 450
    assert r["total_errors"] == 7
    assert r["connections"][0]["requests"] == 200  # highest first
