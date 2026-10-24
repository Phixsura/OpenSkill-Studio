from app.services.app_marketplace_app_live_metrics import get_live_metrics, compute_trend

def test_live():
    r = get_live_metrics(app_id="a1")
    assert r["realtime"]["active_users"] == 142
    assert r["realtime"]["requests_per_sec"] > 0
    assert r["alerts_active"] == 0

def test_trend_up():
    r = compute_trend(values=[10, 12, 14, 20, 22, 25])
    assert r["direction"] == "up"
    assert r["change_pct"] > 0

def test_trend_stable():
    r = compute_trend(values=[50, 51, 50, 49, 50, 51])
    assert r["direction"] == "stable"

def test_trend_short():
    r = compute_trend(values=[42])
    assert r["direction"] == "stable"
