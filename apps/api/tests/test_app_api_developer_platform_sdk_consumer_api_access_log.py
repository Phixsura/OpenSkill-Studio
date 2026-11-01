"""Tests for Endpoint Access Log service."""
from app.services.app_api_developer_platform_sdk_consumer_api_access_log import (
    AccessLog, AccessEntry,
)


class TestAccessLog:
    def _entry(self, rid="r1", cid="c1", eid="ep1", method="GET", status=200, latency=50.0):
        return AccessEntry(rid, "2024-01-01T00:00:00Z", cid, eid, method, status, latency)

    def test_log_and_search(self):
        svc = AccessLog()
        svc.log(self._entry("r1"))
        svc.log(self._entry("r2", cid="c2"))
        results = svc.search(consumer_id="c1")
        assert len(results) == 1
        assert results[0]["request_id"] == "r1"

    def test_search_by_status(self):
        svc = AccessLog()
        svc.log(self._entry("r1", status=200))
        svc.log(self._entry("r2", status=500))
        svc.log(self._entry("r3", status=404))
        errors = svc.search(status_min=400)
        assert len(errors) == 2

    def test_search_by_method(self):
        svc = AccessLog()
        svc.log(self._entry("r1", method="GET"))
        svc.log(self._entry("r2", method="POST"))
        results = svc.search(method="POST")
        assert len(results) == 1

    def test_summary(self):
        svc = AccessLog()
        svc.log(self._entry("r1", status=200, latency=40.0))
        svc.log(self._entry("r2", status=200, latency=60.0))
        svc.log(self._entry("r3", status=500, latency=100.0))
        summary = svc.get_summary()
        assert summary["total"] == 3
        assert summary["success"] == 2
        assert summary["server_errors"] == 1
        assert summary["success_rate"] == 66.7

    def test_summary_by_endpoint(self):
        svc = AccessLog()
        svc.log(self._entry("r1", eid="ep1"))
        svc.log(self._entry("r2", eid="ep2"))
        summary = svc.get_summary(endpoint_id="ep1")
        assert summary["total"] == 1

    def test_top_consumers(self):
        svc = AccessLog()
        for i in range(5):
            svc.log(self._entry(f"r{i}", cid="heavy"))
        svc.log(self._entry("rx", cid="light"))
        top = svc.get_top_consumers(2)
        assert top[0]["consumer_id"] == "heavy"
        assert top[0]["request_count"] == 5

    def test_error_entries(self):
        svc = AccessLog()
        svc.log(self._entry("r1", status=200))
        svc.log(self._entry("r2", status=503))
        errors = svc.get_error_entries()
        assert len(errors) == 1

    def test_eviction(self):
        svc = AccessLog()
        svc._max_entries = 10
        for i in range(15):
            svc.log(self._entry(f"r{i}"))
        assert svc.count() <= 10

    def test_empty_summary(self):
        svc = AccessLog()
        assert svc.get_summary()["total"] == 0

    def test_isolation(self):
        a, b = AccessLog(), AccessLog()
        a.log(self._entry("r1"))
        assert b.count() == 0
