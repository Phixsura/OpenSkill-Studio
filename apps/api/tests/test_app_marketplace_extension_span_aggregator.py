from app.services.app_marketplace_extension_span_aggregator import (
    SpanAggregatorService, Span
)


def _make_spans():
    spans = []
    for i in range(100):
        spans.append(Span(f"t{i}", f"s{i}", "api-gateway", "handle_request",
                          duration_ms=10 + i * 0.5, parent_service=""))
        spans.append(Span(f"t{i}", f"s{i}b", "user-service", "get_user",
                          duration_ms=5 + i * 0.2, parent_service="api-gateway"))
        spans.append(Span(f"t{i}", f"s{i}c", "db", "query",
                          duration_ms=2 + i * 0.1, parent_service="user-service"))
    # Some errors
    for i in range(10):
        spans.append(Span(f"te{i}", f"se{i}", "api-gateway", "handle_request",
                          duration_ms=500, status="error"))
    return spans


def test_ingest():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    assert len(sa.services()) == 3


def test_service_latency():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    lat = sa.service_latency("api-gateway")
    assert lat["count"] == 110  # 100 normal + 10 errors
    assert lat["p50"] > 0
    assert lat["p99"] > lat["p50"]


def test_error_rate():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    rate = sa.service_error_rate("api-gateway")
    assert rate["errors"] == 10
    assert rate["rate"] > 0


def test_no_errors():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    rate = sa.service_error_rate("db")
    assert rate["errors"] == 0


def test_dependency_map():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    deps = sa.dependency_map()
    assert "user-service" in deps["api-gateway"]
    assert "db" in deps["user-service"]


def test_slowest_operations():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    slowest = sa.slowest_operations(3)
    assert len(slowest) == 3
    # First should be the slowest (api-gateway with error spans at 500ms)
    assert slowest[0]["p99_ms"] >= slowest[1]["p99_ms"]


def test_throughput():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    tp = sa.throughput()
    assert tp["api-gateway"] == 110
    assert tp["user-service"] == 100


def test_service_summary():
    sa = SpanAggregatorService()
    sa.ingest_batch(_make_spans())
    summary = sa.service_summary()
    assert len(summary) == 3
    gw = next(s for s in summary if s["service"] == "api-gateway")
    assert gw["error_rate"] > 0
    assert gw["p99"] > 0


def test_empty():
    sa = SpanAggregatorService()
    assert sa.service_latency("none") == {"count": 0}
    assert sa.throughput() == {}
