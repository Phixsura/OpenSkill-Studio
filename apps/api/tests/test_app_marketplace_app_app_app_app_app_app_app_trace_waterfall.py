from app.services.app_marketplace_app_app_app_app_app_app_app_trace_waterfall import build_waterfall

def test_waterfall():
    r = build_waterfall([
        {"service": "gateway", "operation": "handle", "start_ms": 0, "duration_ms": 200, "depth": 0},
        {"service": "api", "operation": "process", "start_ms": 10, "duration_ms": 150, "depth": 1},
        {"service": "db", "operation": "query", "start_ms": 20, "duration_ms": 50, "depth": 2},
    ])
    assert r["span_count"] == 3
    assert r["total_ms"] == 200
    assert r["depth"] == 2
    assert r["spans"][0]["offset_pct"] == 0
    assert r["spans"][0]["width_pct"] == 100.0

def test_empty():
    r = build_waterfall([])
    assert r["span_count"] == 0
    assert r["total_ms"] == 0
