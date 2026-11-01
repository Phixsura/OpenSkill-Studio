from app.services.app_marketplace_app_app_sparkline import build_sparkline

def test_sparkline():
    r = build_sparkline(data=[10, 20, 15, 30, 25], label="Downloads")
    assert r["point_count"] == 5
    assert r["min"] == 10
    assert r["max"] == 30
    assert r["current"] == 25
    assert r["trend"] == "down"
    assert r["points"][0] == 0.0   # min normalized to 0
    assert r["points"][3] == 100.0 # max normalized to 100

def test_empty():
    r = build_sparkline(data=[])
    assert r["trend"] == "flat"
    assert r["points"] == []

def test_flat():
    r = build_sparkline(data=[5, 5, 5])
    assert r["trend"] == "flat"
