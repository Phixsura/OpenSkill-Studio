from app.services.app_marketplace_extension_observability import ObservabilityPipelineService


def test_trace_lifecycle():
    obs = ObservabilityPipelineService()
    ctx = obs.start_trace("handle_request")
    child = obs.start_span(ctx, "db_query")
    obs.end_span(child)
    obs.end_span(ctx)
    trace = obs.get_trace(ctx.trace_id)
    assert len(trace) == 2
    assert trace[0]["operation"] == "handle_request"
    assert trace[1]["parent"] == ctx.span_id


def test_counter():
    obs = ObservabilityPipelineService()
    obs.counter_inc("http_requests", labels={"method": "GET"})
    obs.counter_inc("http_requests", labels={"method": "GET"})
    obs.counter_inc("http_requests", labels={"method": "POST"})
    snapshot = obs.get_metrics_snapshot()
    assert snapshot["counters"]['http_requests{method=GET}'] == 2


def test_gauge():
    obs = ObservabilityPipelineService()
    obs.gauge_set("cpu_usage", 45.5)
    obs.gauge_set("cpu_usage", 62.3)
    snapshot = obs.get_metrics_snapshot()
    assert snapshot["gauges"]["cpu_usage"] == 62.3  # last value


def test_histogram():
    obs = ObservabilityPipelineService()
    for v in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        obs.histogram_observe("latency_ms", v)
    stats = obs.get_histogram_stats("latency_ms")
    assert stats["count"] == 10
    assert stats["mean"] == 55.0
    assert stats["p50"] == 60
    assert stats["min"] == 10
    assert stats["max"] == 100


def test_log_with_trace_context():
    obs = ObservabilityPipelineService()
    ctx = obs.start_trace("api_call")
    record = obs.log("error", "Connection failed", ctx, {"host": "db.local"})
    assert record.trace_id == ctx.trace_id
    assert record.span_id == ctx.span_id
    assert record.attributes["host"] == "db.local"


def test_head_based_sampling():
    obs = ObservabilityPipelineService(sample_rate=0.5)
    sampled = 0
    for _ in range(200):
        ctx = obs.start_trace("test")
        if ctx.sampled:
            sampled += 1
    # ~50% should be sampled (with variance)
    assert 50 < sampled < 150


def test_full_sampling():
    obs = ObservabilityPipelineService(sample_rate=1.0)
    for _ in range(10):
        ctx = obs.start_trace("test")
        obs.end_span(ctx)
    assert obs.get_sampled_trace_count() == 10


def test_no_sampling():
    obs = ObservabilityPipelineService(sample_rate=0.0)
    for _ in range(10):
        obs.start_trace("test")
    assert obs.get_sampled_trace_count() == 0


def test_unsampled_spans_not_stored():
    obs = ObservabilityPipelineService(sample_rate=0.0)
    ctx = obs.start_trace("test")
    obs.start_span(ctx, "child")
    assert obs.get_trace(ctx.trace_id) == []


def test_labeled_metrics():
    obs = ObservabilityPipelineService()
    obs.counter_inc("errors", labels={"service": "auth", "code": "500"})
    obs.counter_inc("errors", labels={"service": "auth", "code": "404"})
    snapshot = obs.get_metrics_snapshot()
    assert len(snapshot["counters"]) == 2
