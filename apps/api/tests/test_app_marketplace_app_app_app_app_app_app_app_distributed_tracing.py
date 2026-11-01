from app.services.app_marketplace_app_app_app_app_app_app_app_distributed_tracing import create_trace, add_span, analyze_trace

def test_trace():
    t = create_trace(service="gateway", operation="GET /api/users")
    root = t["root_span"]
    add_span(t, parent_span=root, service="auth", operation="validate_token", duration_ms=15)
    add_span(t, parent_span=root, service="users", operation="query_db", duration_ms=45, status="ok")
    add_span(t, parent_span=root, service="cache", operation="get", duration_ms=2, status="error")
    a = analyze_trace(t)
    assert a["span_count"] == 4
    assert a["service_count"] == 4
    assert a["has_errors"]
    assert a["error_count"] == 1
    assert a["bottleneck"]["service"] == "users"
    assert a["total_duration_ms"] == 45
