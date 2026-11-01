from app.services.app_marketplace_app_app_app_app_app_app_app_health_predict import predict_health

def test_stable():
    r = predict_health([99.9, 99.9, 99.9, 99.9, 99.9])
    assert r["trend"] == "stable"
    assert not r["will_breach_sla"]

def test_declining():
    r = predict_health([99.9, 99.5, 99.0, 98.5, 98.0])
    assert r["trend"] == "declining"
    assert r["will_breach_sla"]
