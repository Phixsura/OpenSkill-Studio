from app.services.app_marketplace_app_app_app_app_app_app_app_cost_anomaly import detect_anomalies, forecast_monthly

def test_detect_normal():
    r = detect_anomalies([100, 102, 98, 101, 99])
    assert r["status"] == "normal"
    assert len(r["anomalies"]) == 0

def test_detect_spike():
    r = detect_anomalies([100, 100, 100, 100, 100, 100, 800])
    assert r["status"] == "alert"
    assert len(r["anomalies"]) >= 1

def test_forecast():
    r = forecast_monthly(daily_avg=100, days_remaining=15, spent_so_far=1500)
    assert r["projected_total"] == 3000
