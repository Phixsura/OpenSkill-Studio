"""Tests for Consumer API Request Debugger service."""
from app.services.app_api_developer_platform_sdk_consumer_api_request_debugger import (
    RequestDebugger, DebugTrace, TraceSpan,
)


class TestRequestDebugger:
    def _trace(self, tid="t1", status=200, dur=150.0, error=""):
        return DebugTrace(tid, "req-1", "GET", "/api/users", status, dur,
                          spans=[
                              TraceSpan("s1", "auth", 0, 20),
                              TraceSpan("s2", "db_query", 20, 100),
                              TraceSpan("s3", "serialize", 120, 30),
                          ], error=error)

    def test_record_and_get(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace())
        trace = svc.get_trace("t1")
        assert trace is not None
        assert trace["span_count"] == 3
        assert trace["status_code"] == 200

    def test_find_bottleneck(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace())
        bn = svc.find_bottleneck("t1")
        assert bn["bottleneck_span"] == "s2"
        assert bn["name"] == "db_query"
        assert bn["pct_of_total"] > 50

    def test_find_errors(self):
        svc = RequestDebugger()
        trace = self._trace()
        trace.spans[1].status = "error"
        svc.record_trace(trace)
        errors = svc.find_errors("t1")
        assert len(errors) == 1
        assert errors[0]["name"] == "db_query"

    def test_list_traces(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace("t1"))
        svc.record_trace(self._trace("t2"))
        traces = svc.list_traces()
        assert len(traces) == 2

    def test_filter_method(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace("t1"))
        t2 = self._trace("t2")
        t2.method = "POST"
        svc.record_trace(t2)
        traces = svc.list_traces(method="POST")
        assert len(traces) == 1

    def test_error_only(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace("t1"))
        svc.record_trace(self._trace("t2", status=500, error="DB down"))
        traces = svc.list_traces(error_only=True)
        assert len(traces) == 1

    def test_stats(self):
        svc = RequestDebugger()
        svc.record_trace(self._trace("t1", dur=100))
        svc.record_trace(self._trace("t2", dur=200))
        stats = svc.get_stats()
        assert stats["total_traces"] == 2
        assert stats["avg_duration_ms"] == 150.0
        assert stats["max_duration_ms"] == 200

    def test_not_found(self):
        svc = RequestDebugger()
        assert svc.get_trace("missing") is None
        assert svc.find_bottleneck("missing") is None

    def test_nested_children(self):
        svc = RequestDebugger()
        child = TraceSpan("c1", "sub_query", 25, 50, status="error")
        trace = DebugTrace("t1", "r1", "GET", "/api", 200, 100,
                           spans=[TraceSpan("s1", "db", 0, 80, children=[child])])
        svc.record_trace(trace)
        errors = svc.find_errors("t1")
        assert len(errors) == 1
        assert errors[0]["name"] == "sub_query"

    def test_isolation(self):
        a, b = RequestDebugger(), RequestDebugger()
        a.record_trace(self._trace())
        assert b.get_stats()["total_traces"] == 0
