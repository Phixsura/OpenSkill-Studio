"""Tests for Consumer API Request Logger service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_req_logger import (
    RequestLogger, LogEntry,
)


class TestRequestLogger:
    def _entry(self, lid="l1", cid="c1", eid="ep1", method="GET", status=200, latency=50.0):
        return LogEntry(lid, cid, eid, method, status, latency)

    def test_log_and_search(self):
        svc = RequestLogger()
        svc.log(self._entry("l1"))
        svc.log(self._entry("l2", cid="c2"))
        results = svc.search(consumer_id="c1")
        assert len(results) == 1

    def test_auto_level_error(self):
        svc = RequestLogger()
        svc.log(self._entry("l1", status=500))
        results = svc.search(level="error")
        assert len(results) == 1

    def test_auto_level_warn(self):
        svc = RequestLogger()
        svc.log(self._entry("l1", status=404))
        results = svc.search(level="warn")
        assert len(results) == 1

    def test_search_by_method(self):
        svc = RequestLogger()
        svc.log(self._entry("l1", method="GET"))
        svc.log(self._entry("l2", method="POST"))
        results = svc.search(method="POST")
        assert len(results) == 1

    def test_search_by_status_range(self):
        svc = RequestLogger()
        svc.log(self._entry("l1", status=200))
        svc.log(self._entry("l2", status=404))
        svc.log(self._entry("l3", status=500))
        results = svc.search(status_min=400)
        assert len(results) == 2

    def test_summary(self):
        svc = RequestLogger()
        svc.log(self._entry("l1", status=200, latency=40))
        svc.log(self._entry("l2", status=200, latency=60))
        svc.log(self._entry("l3", status=500, latency=100))
        summary = svc.get_summary()
        assert summary["total"] == 3
        assert summary["by_level"]["error"] == 1
        assert summary["avg_latency_ms"] > 0

    def test_tail(self):
        svc = RequestLogger()
        for i in range(20):
            svc.log(self._entry(f"l{i}"))
        tail = svc.tail(5)
        assert len(tail) == 5

    def test_eviction(self):
        svc = RequestLogger()
        svc._max_logs = 10
        for i in range(15):
            svc.log(self._entry(f"l{i}"))
        assert svc.count() <= 10

    def test_invalid_level(self):
        svc = RequestLogger()
        with pytest.raises(ValueError):
            svc.log(LogEntry("l1", "c1", "ep1", "GET", 200, 50, level="trace"))

    def test_isolation(self):
        a, b = RequestLogger(), RequestLogger()
        a.log(self._entry())
        assert b.count() == 0
