from app.services.app_marketplace_app_app_app_app_app_app_app_err_anomaly import detect_error_anomaly, error_rate_trend

def test_anomaly():
    rates = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 5.0]
    r = detect_error_anomaly(rates, sensitivity=2.0)
    assert r["anomaly"]
    assert r["z_score"] > 2

def test_normal():
    rates = [0.1, 0.12, 0.11, 0.1, 0.13, 0.1, 0.11]
    r = detect_error_anomaly(rates)
    assert not r["anomaly"]

def test_trend():
    r = error_rate_trend([0.1, 0.1, 0.1, 0.5, 0.8, 1.0])
    assert r["trend"] == "worsening"
