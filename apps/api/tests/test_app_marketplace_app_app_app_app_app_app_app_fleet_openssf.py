from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_openssf import fleet_openssf_scorecard
def test_ssf():
    r = fleet_openssf_scorecard([{"score": 8.5}, {"score": 7}, {"score": 3}])
    assert r["avg_score"] == 6.2
    assert r["low_score"] == 1
    assert r["grade"] == "B"
