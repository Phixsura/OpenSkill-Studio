from app.services.app_marketplace_app_distributed_tracing import create_trace, add_span, compute_trace_summary

def test_create():
    t = create_trace()
    assert len(t["trace_id"]) == 16
    assert t["status"] == "active"

def test_add_spans():
    t = create_trace(trace_id="abc123")
    t = add_span(trace=t, service="api", operation="handle_request", duration_ms=50)
    t = add_span(trace=t, service="webhook", operation="deliver", duration_ms=100, parent_span_id=t["spans"][0]["span_id"])
    assert len(t["spans"]) == 2

def test_summary():
    t = create_trace(trace_id="x")
    t = add_span(trace=t, service="api", operation="req", duration_ms=50)
    t = add_span(trace=t, service="db", operation="query", duration_ms=30)
    t = add_span(trace=t, service="webhook", operation="send", duration_ms=100, status="error")
    s = compute_trace_summary(trace=t)
    assert s["span_count"] == 3
    assert s["total_duration_ms"] == 180
    assert s["has_errors"]
    assert len(s["services"]) == 3
