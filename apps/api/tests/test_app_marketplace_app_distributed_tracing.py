from app.services.app_marketplace_app_distributed_tracing import create_trace, build_trace_tree

def test_create_root():
    r = create_trace(service="api-gateway", operation="GET /apps")
    assert r["is_root"]
    assert len(r["trace_id"]) == 32
    assert len(r["span_id"]) == 16

def test_create_child():
    r = create_trace(trace_id="abc123", service="catalog", operation="list_apps", parent_span_id="parent1")
    assert not r["is_root"]
    assert r["trace_id"] == "abc123"

def test_tree():
    spans = [
        {"span_id": "s1", "parent_span_id": None, "service": "gateway", "operation": "GET", "duration_ms": 100},
        {"span_id": "s2", "parent_span_id": "s1", "service": "catalog", "operation": "list", "duration_ms": 60},
        {"span_id": "s3", "parent_span_id": "s2", "service": "db", "operation": "query", "duration_ms": 20},
    ]
    r = build_trace_tree(spans=spans)
    assert r["total_spans"] == 3
    assert r["depth"] == 3
    assert len(r["services"]) == 3
    assert r["roots"][0]["span_id"] == "s1"
    assert len(r["roots"][0]["children"]) == 1
