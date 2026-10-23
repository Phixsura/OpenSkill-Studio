from app.services.app_marketplace_app_app_app_app_app_app_app_sparkline import generate_sparkline

def test_sparkline():
    r = generate_sparkline([10, 15, 12, 18, 25, 22, 30])
    assert r["trend"] == "up"
    assert r["min"] == 10
    assert r["max"] == 30
    assert r["current"] == 30
    assert len(r["points"]) > 0
    assert r["change_pct"] == 200.0

def test_flat():
    r = generate_sparkline([50, 50, 50])
    assert r["trend"] == "flat"

def test_empty():
    r = generate_sparkline([])
    assert r["trend"] == "flat"
