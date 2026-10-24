from app.services.app_marketplace_app_app_app_app_app_app_app_req_correlate import (
    generate_correlation_id, correlate_requests, find_slow_traces,
)

def test_correlate():
    spans = [
        {"correlation_id": "c1", "service": "api", "duration_ms": 50},
        {"correlation_id": "c1", "service": "db", "duration_ms": 30},
        {"correlation_id": "c2", "service": "api", "duration_ms": 200},
    ]
    r = correlate_requests(spans)
    assert r["total_traces"] == 2
    assert r["total_spans"] == 3
    c1 = next(t for t in r["traces"] if t["correlation_id"] == "c1")
    assert c1["span_count"] == 2
    assert c1["total_ms"] == 80

def test_slow():
    traces = [{"total_ms": 500}, {"total_ms": 1500}, {"total_ms": 2000}]
    slow = find_slow_traces(traces, 1000)
    assert len(slow) == 2
    assert slow[0]["total_ms"] == 2000

def test_id():
    cid = generate_correlation_id()
    assert cid.startswith("cor_")
    assert len(cid) > 10
