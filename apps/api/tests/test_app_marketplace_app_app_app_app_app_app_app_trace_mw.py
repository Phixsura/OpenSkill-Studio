from app.services.app_marketplace_app_app_app_app_app_app_app_trace_mw import (
    create_trace_context, create_child_span, parse_traceparent,
)

def test_context():
    ctx = create_trace_context()
    assert len(ctx["trace_id"]) == 32
    assert len(ctx["span_id"]) == 16
    assert ctx["header"].startswith("00-")

def test_child():
    parent = create_trace_context()
    child = create_child_span(parent, "db.query")
    assert child["trace_id"] == parent["trace_id"]
    assert child["parent_id"] == parent["span_id"]
    assert child["operation"] == "db.query"

def test_parse():
    r = parse_traceparent("00-abc123def456789000000000abcdef12-1234567890abcdef-01")
    assert r["valid"]
    assert r["sampled"]
    assert not parse_traceparent("bad")["valid"]
