from app.services.app_marketplace_app_app_app_app_app_app_app_trace_analyze import analyze_trace, trace_summary

def test_analyze():
    r = analyze_trace([
        {"service": "api", "operation": "GET /users", "duration_ms": 200, "status": "ok"},
        {"service": "db", "operation": "SELECT", "duration_ms": 150, "status": "ok"},
        {"service": "cache", "operation": "GET", "duration_ms": 5, "status": "error"},
    ])
    assert r["bottleneck"] == "GET /users"
    assert r["service_count"] == 3
    assert r["has_errors"]

def test_summary():
    traces = [{"total_ms": 100, "has_errors": False}, {"total_ms": 200, "has_errors": True}]
    r = trace_summary(traces)
    assert r["avg_duration_ms"] == 150.0
    assert r["error_pct"] == 50
