from app.services.app_marketplace_app_app_app_app_app_app_app_observ_hub import ObservabilityHub

def test_metrics():
    hub = ObservabilityHub()
    hub.record_metric("cpu", 50)
    hub.record_metric("cpu", 60)
    hub.record_metric("cpu", 70)
    s = hub.metric_summary("cpu")
    assert s["count"] == 3
    assert s["min"] == 50
    assert s["max"] == 70

def test_logs_alerts():
    hub = ObservabilityHub()
    hub.record_log("info", "started", "api")
    hub.record_log("error", "crash", "worker")
    d = hub.dashboard()
    assert d["total_logs"] == 2
    assert d["active_alerts"] == 1
    alerts = hub.recent_alerts()
    assert alerts[0]["source"] == "worker"

def test_traces():
    hub = ObservabilityHub()
    hub.record_trace("t1", 5, 200)
    hub.record_trace("t2", 3, 100)
    d = hub.dashboard()
    assert d["total_traces"] == 2
    assert d["avg_trace_ms"] == 150.0

def test_clear():
    hub = ObservabilityHub()
    hub.record_log("error", "bad", "x")
    r = hub.clear_alerts()
    assert r["cleared"] == 1
    assert len(hub.recent_alerts()) == 0
