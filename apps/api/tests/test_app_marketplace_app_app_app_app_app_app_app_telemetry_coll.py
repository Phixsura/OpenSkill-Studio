from app.services.app_marketplace_app_app_app_app_app_app_app_telemetry_coll import (
    record_span, aggregate_spans, top_operations, clear_spans,
)

def test_record_and_aggregate():
    clear_spans()
    record_span("t1", "s1", "GET /api", 50.0)
    record_span("t1", "s2", "GET /api", 150.0, status="error")
    record_span("t2", "s3", "POST /api", 80.0)
    r = aggregate_spans("GET /api")
    assert r["count"] == 2
    assert r["avg_ms"] == 100.0
    assert r["error_count"] == 1
    clear_spans()

def test_top_ops():
    clear_spans()
    for _ in range(5):
        record_span("t", "s", "GET /", 10.0)
    for _ in range(3):
        record_span("t", "s", "POST /", 20.0)
    ops = top_operations()
    assert ops[0]["operation"] == "GET /"
    assert ops[0]["count"] == 5
    clear_spans()
