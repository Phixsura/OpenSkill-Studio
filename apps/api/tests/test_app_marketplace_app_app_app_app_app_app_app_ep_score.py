from app.services.app_marketplace_app_app_app_app_app_app_app_ep_score import score_endpoint, rank_endpoints

def test_score():
    r = score_endpoint({"endpoint": "/api/users", "availability_pct": 99.99,
                         "p99_ms": 100, "error_rate_pct": 0.1, "rps": 500})
    assert r["grade"] == "A"
    assert r["score"] > 90

def test_rank():
    r = rank_endpoints([
        {"endpoint": "/slow", "availability_pct": 95, "p99_ms": 2000, "error_rate_pct": 10, "rps": 10},
        {"endpoint": "/fast", "availability_pct": 99.99, "p99_ms": 50, "error_rate_pct": 0, "rps": 1000},
    ])
    assert r[0]["endpoint"] == "/slow"  # worst first
    assert r[1]["endpoint"] == "/fast"
