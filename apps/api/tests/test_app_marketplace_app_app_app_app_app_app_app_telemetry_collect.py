from app.services.app_marketplace_app_app_app_app_app_app_app_telemetry_collect import TelemetryCollector

def test_counter():
    tc = TelemetryCollector()
    tc.increment("requests", 1, {"method": "GET"})
    tc.increment("requests", 1, {"method": "GET"})
    tc.increment("requests", 1, {"method": "POST"})
    snap = tc.snapshot()
    assert snap["counters"]["requests{method=GET}"] == 2
    assert snap["counters"]["requests{method=POST}"] == 1

def test_gauge():
    tc = TelemetryCollector()
    tc.gauge("cpu_pct", 75.5)
    tc.gauge("cpu_pct", 80.0)
    snap = tc.snapshot()
    assert snap["gauges"]["cpu_pct"] == 80.0

def test_histogram():
    tc = TelemetryCollector()
    for v in [10, 20, 30, 40, 50, 100, 200, 300, 400, 500]:
        tc.histogram("latency_ms", v)
    snap = tc.snapshot()
    h = snap["histograms"]["latency_ms"]
    assert h["count"] == 10
    assert h["min"] == 10
    assert h["max"] == 500
    assert h["p50"] == 100

def test_reset():
    tc = TelemetryCollector()
    tc.increment("a")
    tc.gauge("b", 1)
    r = tc.reset()
    assert r["flushed"] == 2
    assert tc.snapshot()["total_metrics"] == 0
