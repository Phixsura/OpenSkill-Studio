from app.services.app_marketplace_app_app_app_app_app_app_app_inc_count_trend import incident_count_trend
def test_worsening():
    r = incident_count_trend([{"incidents": 1}, {"incidents": 2}, {"incidents": 5}, {"incidents": 8}])
    assert r["trend"] == "worsening"
def test_improving():
    r = incident_count_trend([{"incidents": 10}, {"incidents": 8}, {"incidents": 2}, {"incidents": 1}])
    assert r["trend"] == "improving"
