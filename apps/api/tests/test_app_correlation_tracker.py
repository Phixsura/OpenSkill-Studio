"""Tests for App Correlation Tracker — spans, traces, parent-child."""

import pytest

from app.services.app_correlation_tracker import AppCorrelationTracker


class TestStartSpan:
    def test_start(self):
        t = AppCorrelationTracker()
        s = t.start_span("inst-1", "s1", "trace-1", "api-gw", "GET /users", now=1000.0)
        assert s.span_id == "s1"
        assert s.service == "api-gw"
        assert s.ended_at is None

    def test_with_parent(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "handler")
        s = t.start_span("inst-1", "s2", "t1", "db", "query", parent_span_id="s1")
        assert s.parent_span_id == "s1"

    def test_duplicate(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op")
        with pytest.raises(ValueError, match="already exists"):
            t.start_span("inst-1", "s1", "t1", "api", "op2")


class TestEndSpan:
    def test_end(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op", now=1000.0)
        s = t.end_span("inst-1", "s1", now=1002.0)
        assert s.status == "ok"
        assert s.duration_ms == 2000.0

    def test_end_with_error(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op")
        s = t.end_span("inst-1", "s1", status="error")
        assert s.status == "error"

    def test_double_end(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op")
        t.end_span("inst-1", "s1")
        with pytest.raises(ValueError, match="already ended"):
            t.end_span("inst-1", "s1")


class TestGetTrace:
    def test_trace_order(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s2", "t1", "db", "query", now=1001.0)
        t.start_span("inst-1", "s1", "t1", "api", "handler", now=1000.0)
        trace = t.get_trace("inst-1", "t1")
        assert [s.span_id for s in trace] == ["s1", "s2"]

    def test_empty_trace(self):
        t = AppCorrelationTracker()
        assert t.get_trace("inst-1", "nope") == []


class TestGetChildren:
    def test_children(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "root", "t1", "api", "handler")
        t.start_span("inst-1", "child1", "t1", "db", "query", parent_span_id="root")
        t.start_span("inst-1", "child2", "t1", "cache", "get", parent_span_id="root")
        children = t.get_children("inst-1", "root")
        assert len(children) == 2

    def test_no_children(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op")
        assert t.get_children("inst-1", "s1") == []


class TestGenerateTraceId:
    def test_unique(self):
        t = AppCorrelationTracker()
        ids = {t.generate_trace_id() for _ in range(100)}
        assert len(ids) == 100


class TestIsolation:
    def test_cross_installation(self):
        t = AppCorrelationTracker()
        t.start_span("inst-1", "s1", "t1", "api", "op")
        with pytest.raises(KeyError):
            t.get_span("inst-2", "s1")
