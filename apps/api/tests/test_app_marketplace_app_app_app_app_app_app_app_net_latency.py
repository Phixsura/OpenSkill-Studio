from app.services.app_marketplace_app_app_app_app_app_app_app_net_latency import measure_latency

def test_latency():
    measurements = [
        {"from": "api", "to": "db", "latency_ms": 5},
        {"from": "api", "to": "db", "latency_ms": 8},
        {"from": "api", "to": "cache", "latency_ms": 1},
        {"from": "web", "to": "api", "latency_ms": 20},
    ]
    r = measure_latency(measurements)
    assert r["total_pairs"] == 3
    assert r["highest_latency"] == "web→api"
    db_pair = next(p for p in r["pairs"] if p["pair"] == "api→db")
    assert db_pair["avg_ms"] == 6.5
    assert db_pair["samples"] == 2
