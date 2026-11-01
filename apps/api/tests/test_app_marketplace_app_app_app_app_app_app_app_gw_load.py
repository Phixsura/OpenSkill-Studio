from app.services.app_marketplace_app_app_app_app_app_app_app_gw_load import calculate_load

def test_low():
    r = calculate_load(100, 10000, 500, 50000, 20)
    assert r["status"] == "low"

def test_high():
    r = calculate_load(8000, 10000, 40000, 50000, 75)
    assert r["status"] == "high"

def test_overloaded():
    r = calculate_load(9500, 10000, 48000, 50000, 95)
    assert r["status"] == "overloaded"
