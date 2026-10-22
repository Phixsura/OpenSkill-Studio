from app.services.app_marketplace_app_error_tracking import classify_error, aggregate_errors, build_error_trend

def test_classify_500():
    r = classify_error(status_code=500, message="Internal")
    assert r["category"] == "server_error"
    assert r["severity"] == "high"

def test_classify_503():
    r = classify_error(status_code=503, message="Unavailable")
    assert r["severity"] == "critical"

def test_classify_429():
    r = classify_error(status_code=429, message="Too many")
    assert r["category"] == "rate_limit"

def test_aggregate():
    errors = [{"category": "server_error", "status_code": 500, "severity": "high"},
              {"category": "server_error", "status_code": 503, "severity": "critical"},
              {"category": "client_error", "status_code": 400, "severity": "low"}]
    r = aggregate_errors(errors=errors)
    assert r["total"] == 3
    assert r["critical_count"] == 1

def test_trend_stable():
    hourly = [{"count": 5}] * 10
    r = build_error_trend(hourly_counts=hourly)
    assert r["trend"] == "stable"

def test_trend_rising():
    hourly = [{"count": 1}] * 7 + [{"count": 50}] * 3
    r = build_error_trend(hourly_counts=hourly)
    assert r["trend"] == "rising"
