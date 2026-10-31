from app.services.app_marketplace_app_app_app_app_app_app_app_net_latency import build_latency_map

def test_map():
    r = build_latency_map([
        {"source": "api", "destination": "db", "latency_ms": 5},
        {"source": "api", "destination": "db", "latency_ms": 8},
        {"source": "api", "destination": "db", "latency_ms": 3},
        {"source": "web", "destination": "api", "latency_ms": 15},
    ])
    assert r["total_pairs"] == 2
    assert r["total_measurements"] == 4
    db_pair = [p for p in r["pairs"] if p["destination"] == "db"][0]
    assert db_pair["samples"] == 3
    assert db_pair["min_ms"] == 3
