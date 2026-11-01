from app.services.app_marketplace_app_app_app_app_app_app_app_ep_usage_trend import calculate_trend, top_growing

def test_growing():
    r = calculate_trend([{"requests": 100}, {"requests": 110}, {"requests": 150}, {"requests": 200}])
    assert r["trend"] == "growing"
    assert r["change_pct"] > 0

def test_stable():
    r = calculate_trend([{"requests": 100}, {"requests": 102}, {"requests": 98}, {"requests": 101}])
    assert r["trend"] == "stable"

def test_top():
    eps = [
        {"endpoint": "/fast", "snapshots": [{"requests": 100}, {"requests": 100}]},
        {"endpoint": "/growing", "snapshots": [{"requests": 100}, {"requests": 200}]},
    ]
    r = top_growing(eps)
    assert len(r) == 1
    assert r[0]["endpoint"] == "/growing"
