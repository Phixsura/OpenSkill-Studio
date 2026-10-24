from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_observ import analyze_mesh_traffic

def test_analyze():
    r = analyze_mesh_traffic([
        {"source": "web", "destination": "api", "latency_ms": 10, "status": 200},
        {"source": "web", "destination": "api", "latency_ms": 15, "status": 200},
        {"source": "api", "destination": "db", "latency_ms": 5, "status": 200},
        {"source": "api", "destination": "db", "latency_ms": 100, "status": 500},
    ])
    assert r["total_flows"] == 4
    assert r["unique_pairs"] == 2
    assert r["total_errors"] == 1
    assert r["pairs"][0]["source"] == "web"
    assert r["pairs"][0]["avg_ms"] == 12.5
