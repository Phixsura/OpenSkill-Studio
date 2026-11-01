from app.services.app_marketplace_app_app_app_app_app_app_app_usage_trends import compute_trends

def test_growing():
    data = [{"value": v} for v in [100, 110, 120, 130, 150, 180, 200, 250]]
    r = compute_trends(data)
    assert r["trend"] == "growing"
    assert r["change_pct"] > 0
    assert r["peak"] == 250

def test_stable():
    data = [{"value": v} for v in [100, 102, 98, 101, 99, 103]]
    r = compute_trends(data)
    assert r["trend"] == "stable"
