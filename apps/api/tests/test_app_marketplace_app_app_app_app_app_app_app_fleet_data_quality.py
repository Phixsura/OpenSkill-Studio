from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_quality import fleet_data_quality
def test_dq():
    r = fleet_data_quality([{"quality_score": 95}, {"quality_score": 85}, {"quality_score": 60}])
    assert r["good"] == 1
    assert r["poor"] == 1
    assert r["avg_score"] == 80.0
    assert not r["high_quality"]
