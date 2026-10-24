from app.services.app_marketplace_app_app_app_app_app_app_app_alert_freq_trend import alert_freq_trend
def test_noisier():
    r = alert_freq_trend([{"alerts": 5}, {"alerts": 6}, {"alerts": 20}, {"alerts": 25}])
    assert r["trend"] == "noisier"
def test_quieter():
    r = alert_freq_trend([{"alerts": 30}, {"alerts": 25}, {"alerts": 5}, {"alerts": 3}])
    assert r["trend"] == "quieter"
