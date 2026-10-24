from app.services.app_marketplace_app_app_app_app_app_app_app_api_dep_graph import build_api_graph

def test_graph():
    r = build_api_graph([
        {"caller": "web", "callee": "api", "count": 1000, "total_latency_ms": 50000},
        {"caller": "api", "callee": "db", "count": 5000, "total_latency_ms": 25000},
        {"caller": "api", "callee": "cache", "count": 3000, "total_latency_ms": 3000},
    ])
    assert r["node_count"] == 4
    assert r["edge_count"] == 3
    assert r["total_calls"] == 9000
    assert r["edges"][0]["source"] == "api"  # most calls
