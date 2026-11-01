from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_headroom import calculate_headroom

def test_headroom():
    r = calculate_headroom([
        {"name": "api", "current_rps": 800, "max_rps": 1000},
        {"name": "worker", "current_rps": 200, "max_rps": 500},
    ])
    assert r["bottleneck"] == "api"
    assert r["min_headroom_pct"] == 20.0
    assert r["services"][0]["status"] == "warning"
    assert r["services"][1]["status"] == "ok"
