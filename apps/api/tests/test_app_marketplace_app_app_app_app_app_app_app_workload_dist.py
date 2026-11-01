from app.services.app_marketplace_app_app_app_app_app_app_app_workload_dist import analyze_distribution

def test_balanced():
    r = analyze_distribution([
        {"name": "n1", "load_pct": 50}, {"name": "n2", "load_pct": 55},
        {"name": "n3", "load_pct": 48},
    ])
    assert r["balanced"]
    assert r["spread"] < 30

def test_imbalanced():
    r = analyze_distribution([
        {"name": "n1", "load_pct": 95}, {"name": "n2", "load_pct": 20},
        {"name": "n3", "load_pct": 30},
    ])
    assert not r["balanced"]
    assert r["hotspot"] == "n1"
