from app.services.app_marketplace_app_app_app_app_app_app_app_cost_center import allocate_by_dimension, monthly_trend

def test_allocate():
    r = allocate_by_dimension([
        {"team": "platform", "amount": 500}, {"team": "platform", "amount": 300},
        {"team": "data", "amount": 200},
    ], "team")
    assert r["total"] == 1000
    assert r["top"] == "platform"
    assert r["groups"] == 2

def test_trend():
    r = monthly_trend([{"total": 800}, {"total": 1000}])
    assert r["trend"] == "up"
    assert r["delta"] == 200
    assert r["pct_change"] == 25.0
