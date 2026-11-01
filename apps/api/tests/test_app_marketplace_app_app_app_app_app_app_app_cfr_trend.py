from app.services.app_marketplace_app_app_app_app_app_app_app_cfr_trend import cfr_trend
def test_improving():
    r = cfr_trend([{"cfr_pct": 20}, {"cfr_pct": 15}, {"cfr_pct": 5}, {"cfr_pct": 3}])
    assert r["trend"] == "improving"
