from app.services.app_marketplace_app_app_sparkline import generate_sparkline

def test_sparkline():
    r = generate_sparkline(values=[10, 20, 15, 25, 30], label="Installs")
    assert len(r["points"]) == 5
    assert r["current"] == 30
    assert r["trend"] == "up"
    assert r["min"] == 10
    assert r["max"] == 30
    assert r["label"] == "Installs"

def test_flat():
    r = generate_sparkline(values=[5, 5, 5])
    assert r["trend"] == "flat"

def test_empty():
    r = generate_sparkline(values=[])
    assert r["empty"]
