from app.services.app_marketplace_app_app_app_app_app_app_app_trace_corr import correlate_traces, find_slow_traces

def test_correlate():
    r = correlate_traces([
        {"trace_id": "t1", "service": "api", "start_ms": 0, "duration_ms": 100},
        {"trace_id": "t1", "service": "db", "start_ms": 10, "duration_ms": 50},
        {"trace_id": "t2", "service": "api", "start_ms": 0, "duration_ms": 200},
    ])
    assert r["total_traces"] == 2
    assert r["total_spans"] == 3
    assert r["traces"][0]["trace_id"] == "t2"  # slowest first

def test_slow():
    traces = [{"trace_id": "t1", "duration_ms": 500}, {"trace_id": "t2", "duration_ms": 2000}]
    r = find_slow_traces(traces, threshold_ms=1000)
    assert len(r) == 1
    assert r[0]["trace_id"] == "t2"
