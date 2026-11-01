from app.services.app_marketplace_app_app_app_app_app_app_app_uptime_trend import uptime_trend
def test_improving():
    r = uptime_trend([{"uptime_pct": 99.0}, {"uptime_pct": 99.5}, {"uptime_pct": 99.9}, {"uptime_pct": 99.99}])
    assert r["trend"] == "improving"
def test_stable():
    r = uptime_trend([{"uptime_pct": 99.9}, {"uptime_pct": 99.9}, {"uptime_pct": 99.9}])
    assert r["trend"] == "stable"
