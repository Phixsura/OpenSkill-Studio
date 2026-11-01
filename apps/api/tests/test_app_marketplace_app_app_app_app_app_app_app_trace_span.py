from app.services.app_marketplace_app_app_app_app_app_app_app_trace_span import collect_spans, find_bottleneck, trace_depth

def test_collect():
    r = collect_spans([
        {"span_id": "s1", "service": "api", "duration_ms": 50},
        {"span_id": "s2", "service": "api", "duration_ms": 30, "parent_id": "s1"},
        {"span_id": "s3", "service": "db", "duration_ms": 20, "parent_id": "s2"},
    ])
    assert r["total_spans"] == 3
    assert r["services"] == 2
    assert r["root_spans"] == 1

def test_bottleneck():
    r = find_bottleneck([
        {"span_id": "s1", "service": "api", "operation": "handle", "duration_ms": 50},
        {"span_id": "s2", "service": "db", "operation": "query", "duration_ms": 200},
    ])
    assert r["service"] == "db"
    assert r["duration_ms"] == 200

def test_depth():
    d = trace_depth([
        {"span_id": "a"}, {"span_id": "b", "parent_id": "a"},
        {"span_id": "c", "parent_id": "b"},
    ])
    assert d == 3
