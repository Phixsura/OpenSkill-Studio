from app.services.app_marketplace_extension_otel_exporter import ExtOtelExporterService

def test_trace_and_span():
    svc = ExtOtelExporterService()
    root = svc.start_trace("ext-1", "handle_request")
    child = svc.start_span(root.trace_id, "db_query", root.span_id, "ext-1")
    assert child is not None
    svc.end_span(root.trace_id, child.span_id)
    svc.end_span(root.trace_id, root.span_id)
    trace = svc.get_trace(root.trace_id)
    assert len(trace) == 2
    assert trace[1].parent_span_id == root.span_id

def test_duration():
    svc = ExtOtelExporterService()
    span = svc.start_trace("ext-1", "op")
    import time; time.sleep(0.01)
    svc.end_span(span.trace_id, span.span_id)
    assert span.duration_ms > 0

def test_invalid_trace():
    svc = ExtOtelExporterService()
    assert svc.start_span("nonexistent", "child", "p", "ext-1") is None
