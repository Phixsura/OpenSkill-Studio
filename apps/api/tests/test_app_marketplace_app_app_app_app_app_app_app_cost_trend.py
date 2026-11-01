from app.services.app_marketplace_app_app_app_app_app_app_app_cost_trend import analyze_cost_trend

def test_increasing():
    r = analyze_cost_trend([
        {"month": "Jan", "cost": 1000}, {"month": "Feb", "cost": 1100},
        {"month": "Mar", "cost": 1200}, {"month": "Apr", "cost": 1400},
    ])
    assert r["trend"] == "increasing"
    assert r["change_pct"] > 0

def test_stable():
    r = analyze_cost_trend([
        {"cost": 1000}, {"cost": 1010}, {"cost": 990}, {"cost": 1005},
    ])
    assert r["trend"] == "stable"
