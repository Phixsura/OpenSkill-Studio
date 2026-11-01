from app.services.app_marketplace_app_app_app_app_app_app_app_pod_scaler import simulate_hpa, forecast_pods

def test_scale_up():
    r = simulate_hpa(3, 90.0, 50.0, min_pods=1, max_pods=10)
    assert r["action"] == "scale_up"
    assert r["desired_pods"] > 3

def test_stable():
    r = simulate_hpa(5, 50.0, 50.0)
    assert r["action"] == "stable"

def test_forecast():
    r = forecast_pods(2, [1.0, 2.0, 3.0], 70.0, 0.5)
    assert len(r) == 3
    assert r[2]["estimated_pods"] > r[0]["estimated_pods"]
