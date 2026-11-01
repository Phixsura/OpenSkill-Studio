from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_reliability import fleet_reliability_score
def test_reliability():
    r = fleet_reliability_score({"uptime_pct": 99.99, "mttr_min": 30, "cfr_pct": 2})
    assert r["score"] == 95.49
    assert r["grade"] == "Gold"
