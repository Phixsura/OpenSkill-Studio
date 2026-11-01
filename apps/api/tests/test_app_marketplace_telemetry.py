from app.services.app_marketplace_telemetry import TelemetryCollector


def test_opt_in_required():
    tc = TelemetryCollector()
    assert tc.record("ext-1", "page_view", org_id="org-1") is False
    tc.opt_in("org-1")
    assert tc.record("ext-1", "page_view", org_id="org-1") is True


def test_record_without_org():
    tc = TelemetryCollector()
    assert tc.record("ext-2", "startup", value=150.0) is True


def test_aggregates():
    tc = TelemetryCollector()
    tc.record("ext-3", "latency", 100.0)
    tc.record("ext-3", "latency", 200.0)
    tc.record("ext-3", "latency", 300.0)
    agg = tc.get_aggregates("ext-3", "latency")
    assert agg["count"] == 3
    assert agg["min"] == 100.0
    assert agg["max"] == 300.0
    assert agg["avg"] == 200.0


def test_counters():
    tc = TelemetryCollector()
    tc.increment("ext-4", "api_calls", 5)
    tc.increment("ext-4", "api_calls", 3)
    assert tc.get_counter("ext-4", "api_calls") == 8


def test_top_events():
    tc = TelemetryCollector()
    for _ in range(10):
        tc.record("ext-5", "click")
    for _ in range(5):
        tc.record("ext-5", "scroll")
    for _ in range(2):
        tc.record("ext-5", "submit")
    top = tc.get_top_events("ext-5")
    assert top[0] == ("click", 10)


def test_dashboard():
    tc = TelemetryCollector()
    tc.record("ext-6", "init", 1.0)
    tc.record("ext-6", "render", 5.0)
    tc.record("ext-6", "init", 2.0)
    tc.increment("ext-6", "errors", 3)
    dash = tc.get_dashboard("ext-6")
    assert dash["total_events"] == 3
    assert dash["unique_event_types"] == 2
    assert dash["counters"]["errors"] == 3


def test_opt_out():
    tc = TelemetryCollector()
    tc.opt_in("org-x")
    tc.opt_out("org-x")
    assert tc.is_opted_in("org-x") is False
