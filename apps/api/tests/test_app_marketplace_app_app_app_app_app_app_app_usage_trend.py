from app.services.app_marketplace_app_app_app_app_app_app_app_usage_trend import analyze_trend

def test_growing():
    r = analyze_trend([10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36])
    assert r["trend"] == "growing"
    assert r["growth_pct"] > 0

def test_stable():
    r = analyze_trend([50, 51, 49, 50, 52, 48, 50, 51, 49, 50, 52, 48, 50, 51])
    assert r["trend"] == "stable"
