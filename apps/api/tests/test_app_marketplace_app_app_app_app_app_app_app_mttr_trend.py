from app.services.app_marketplace_app_app_app_app_app_app_app_mttr_trend import mttr_trend
def test_improving():
    r = mttr_trend([{"mttr_min": 60}, {"mttr_min": 50}, {"mttr_min": 20}, {"mttr_min": 15}])
    assert r["trend"] == "improving"
