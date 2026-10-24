from app.services.app_marketplace_app_app_tracing_context import create_trace, create_span, build_trace_waterfall

def test_create_trace():
    r = create_trace()
    assert len(r["trace_id"]) == 32
    assert r["traceparent"].startswith("00-")

def test_create_span():
    r = create_span(trace_id="abc", operation="GET /apps", service="api-gateway")
    assert r["operation"] == "GET /apps"
    assert r["service"] == "api-gateway"

def test_waterfall():
    spans = [
        {"span_id": "s1", "parent_span_id": None, "service": "gateway", "started_at": "2026-01-01T00:00:00Z"},
        {"span_id": "s2", "parent_span_id": "s1", "service": "api", "started_at": "2026-01-01T00:00:01Z"},
        {"span_id": "s3", "parent_span_id": "s2", "service": "db", "started_at": "2026-01-01T00:00:02Z"},
    ]
    r = build_trace_waterfall(spans=spans)
    assert r["total_spans"] == 3
    assert r["root_spans"] == 1
    assert r["max_depth"] == 3
    assert len(r["services"]) == 3
