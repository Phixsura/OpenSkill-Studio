from app.services.app_marketplace_extension_observability import (
    ObservabilityService,
)


def test_start_trace():
    svc = ObservabilityService()
    span = svc.start_trace("handle_request", {"method": "GET"})
    assert span.trace_id.startswith("tr_")
    assert span.name == "handle_request"


def test_parent_child_spans():
    svc = ObservabilityService()
    root = svc.start_trace("request")
    child = svc.start_span(root.trace_id, "db_query", parent_id=root.span_id)
    assert child.parent_id == root.span_id
    spans = svc.get_trace(root.trace_id)
    assert len(spans) == 2


def test_end_span_timing():
    svc = ObservabilityService()
    root = svc.start_trace("task")
    svc.end_span(root.trace_id, root.span_id)
    assert root.duration_ms >= 0
    assert root.status == "ok"


def test_error_span():
    svc = ObservabilityService()
    root = svc.start_trace("failing")
    svc.end_span(root.trace_id, root.span_id, status="error")
    errors = svc.get_error_spans(root.trace_id)
    assert len(errors) == 1


def test_add_event():
    svc = ObservabilityService()
    root = svc.start_trace("task")
    svc.add_event(root.trace_id, root.span_id, "cache_miss", {"key": "user:1"})
    assert len(root.events) == 1
    assert root.events[0]["name"] == "cache_miss"


def test_trace_tree():
    svc = ObservabilityService()
    root = svc.start_trace("request")
    c1 = svc.start_span(root.trace_id, "auth", parent_id=root.span_id)
    c2 = svc.start_span(root.trace_id, "handler", parent_id=root.span_id)
    svc.start_span(root.trace_id, "db", parent_id=c2.span_id)
    for s in svc.get_trace(root.trace_id):
        svc.end_span(root.trace_id, s.span_id)
    tree = svc.get_trace_tree(root.trace_id)
    assert tree["name"] == "request"
    assert len(tree["children"]) == 2
    handler = next(c for c in tree["children"] if c["name"] == "handler")
    assert len(handler["children"]) == 1


def test_slow_spans():
    svc = ObservabilityService()
    root = svc.start_trace("req")
    child = svc.start_span(root.trace_id, "slow_query", parent_id=root.span_id)
    # Manually set duration
    child.duration_ms = 250
    svc.end_span(root.trace_id, root.span_id)
    slow = svc.get_slow_spans(root.trace_id, threshold_ms=100)
    assert any(s.name == "slow_query" for s in slow)
