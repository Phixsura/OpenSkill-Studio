from app.services.app_marketplace_app_app_app_app_app_app_app_trace_viewer import build_trace_tree, find_slow_spans

def test_tree():
    spans = [
        {"trace_id": "t1", "span_id": "s1", "parent_id": None, "operation": "GET /", "duration_ms": 200},
        {"trace_id": "t1", "span_id": "s2", "parent_id": "s1", "operation": "DB query", "duration_ms": 150},
        {"trace_id": "t1", "span_id": "s3", "parent_id": "s1", "operation": "Cache get", "duration_ms": 5},
    ]
    r = build_trace_tree(spans)
    assert r["span_count"] == 3
    assert r["root_span"] == "s1"
    assert r["depth"] == 2
    assert r["critical_span"] == "GET /"

def test_slow():
    spans = [
        {"operation": "fast", "duration_ms": 5},
        {"operation": "slow", "duration_ms": 500},
        {"operation": "medium", "duration_ms": 100},
    ]
    slow = find_slow_spans(spans, 100)
    assert len(slow) == 2
    assert slow[0]["operation"] == "slow"
