from app.services.app_marketplace_app_app_app_app_app_app_app_avail_predict import predict_availability

def test_stable():
    r = predict_availability([99.9, 99.9, 99.9, 99.9, 99.9])
    assert r["trend"] == "stable"
    assert not r["will_breach"]

def test_declining():
    r = predict_availability([99.9, 99.5, 99.0, 98.5, 98.0])
    assert r["trend"] == "declining"
