from app.services.app_marketplace_app_health_trends import compute_health_trend, build_health_report, identify_correlations

def test_degrading():
    data = [{"latency": 100}] * 5 + [{"latency": 200}] * 5
    r = compute_health_trend(data_points=data, metric="latency")
    assert r["trend"] == "degrading"

def test_improving():
    data = [{"errors": 50}] * 5 + [{"errors": 10}] * 5
    r = compute_health_trend(data_points=data, metric="errors")
    assert r["trend"] == "improving"

def test_stable():
    data = [{"cpu": 50}] * 10
    r = compute_health_trend(data_points=data, metric="cpu")
    assert r["trend"] == "stable"

def test_report():
    trends = [{"trend": "degrading"}, {"trend": "improving"}, {"trend": "stable"}]
    r = build_health_report(trends=trends)
    assert r["needs_attention"]

def test_correlations():
    metrics = {"latency": [100, 150, 200], "errors": [1, 3, 5]}
    r = identify_correlations(metrics=metrics)
    assert len(r) == 1
    assert r[0]["direction"] == "positive"
