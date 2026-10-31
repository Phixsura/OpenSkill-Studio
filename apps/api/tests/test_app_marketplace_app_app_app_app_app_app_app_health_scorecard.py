from app.services.app_marketplace_app_app_app_app_app_app_app_health_scorecard import compute_scorecard

def test_scorecard():
    r = compute_scorecard({"availability": 99, "latency": 85, "errors": 95, "saturation": 60})
    assert r["grade"] == "B"
    assert r["weakest"] == "saturation"
    assert r["weakest_score"] == 60
