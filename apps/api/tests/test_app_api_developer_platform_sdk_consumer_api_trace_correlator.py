"""Tests for Consumer API Trace Correlation service."""
from app.services.app_api_developer_platform_sdk_consumer_api_trace_correlator import (
    TraceCorrelator, Span,
)


class TestTraceCorrelator:
    def test_record_and_get_trace(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="auth", operation="verify", duration_ms=20))
        svc.record_span(Span("s2", "t1", parent_span_id="s1", service_name="db", operation="query", duration_ms=50))
        trace = svc.get_trace("t1")
        assert trace is not None
        assert trace["span_count"] == 2
        assert trace["service_count"] == 2

    def test_span_tree(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="gateway", operation="route", start_time=0, duration_ms=100))
        svc.record_span(Span("s2", "t1", parent_span_id="s1", service_name="auth", operation="check", start_time=5, duration_ms=20))
        svc.record_span(Span("s3", "t1", parent_span_id="s1", service_name="api", operation="handle", start_time=30, duration_ms=60))
        tree = svc.get_span_tree("t1")
        assert len(tree) == 1  # one root
        assert len(tree[0]["children"]) == 2

    def test_critical_path(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="gw", operation="route", duration_ms=10))
        svc.record_span(Span("s2", "t1", service_name="db", operation="query", duration_ms=80))
        svc.record_span(Span("s3", "t1", service_name="cache", operation="get", duration_ms=5))
        path = svc.find_critical_path("t1")
        assert path[0]["operation"] == "query"  # slowest first

    def test_error_detection(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="api", status="ok", duration_ms=50))
        svc.record_span(Span("s2", "t1", service_name="db", status="error", duration_ms=100))
        trace = svc.get_trace("t1")
        assert trace["has_errors"] is True
        assert trace["error_count"] == 1

    def test_correlate(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="auth"))
        svc.record_span(Span("s2", "t1", service_name="users"))
        svc.record_span(Span("s3", "t2", service_name="auth"))
        svc.record_span(Span("s4", "t2", service_name="orders"))
        result = svc.correlate("t1", "t2")
        assert result["common_services"] == ["auth"]

    def test_generate_ids(self):
        svc = TraceCorrelator()
        tid = svc.generate_trace_id()
        sid = svc.generate_span_id()
        assert len(tid) == 32
        assert len(sid) == 16

    def test_list_traces(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="a", duration_ms=10))
        svc.record_span(Span("s2", "t2", service_name="b", duration_ms=20))
        traces = svc.list_traces()
        assert len(traces) == 2

    def test_stats(self):
        svc = TraceCorrelator()
        svc.record_span(Span("s1", "t1", service_name="auth"))
        svc.record_span(Span("s2", "t1", service_name="db"))
        svc.record_span(Span("s3", "t2", service_name="auth"))
        stats = svc.get_stats()
        assert stats["total_traces"] == 2
        assert stats["total_spans"] == 3
        assert stats["unique_services"] == 2

    def test_not_found(self):
        svc = TraceCorrelator()
        assert svc.get_trace("missing") is None

    def test_isolation(self):
        a, b = TraceCorrelator(), TraceCorrelator()
        a.record_span(Span("s1", "t1", service_name="x"))
        assert b.get_stats()["total_traces"] == 0
