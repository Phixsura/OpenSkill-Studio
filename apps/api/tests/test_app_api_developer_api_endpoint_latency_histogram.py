import pytest
from app.services.app_api_developer_api_endpoint_latency_histogram import AppAPIDeveloperAPIEndpointLatencyHistogram

class TestLatencyHistogram:
    def test_record(self):
        h = AppAPIDeveloperAPIEndpointLatencyHistogram()
        r = h.record("inst-1", "/api/users", 45)
        assert r.total == 1
        assert r.avg_ms == 45.0

    def test_buckets(self):
        h = AppAPIDeveloperAPIEndpointLatencyHistogram()
        for _ in range(100): h.record("inst-1", "/api/a", 30)
        r = h.get("inst-1", "/api/a")
        assert r.buckets[50] == 100

    def test_p99(self):
        h = AppAPIDeveloperAPIEndpointLatencyHistogram()
        for _ in range(99): h.record("inst-1", "/api/a", 30)
        h.record("inst-1", "/api/a", 3000)
        r = h.get("inst-1", "/api/a")
        assert r.p99_bucket == 50

    def test_slowest(self):
        h = AppAPIDeveloperAPIEndpointLatencyHistogram()
        for _ in range(10): h.record("inst-1", "/fast", 10)
        for _ in range(10): h.record("inst-1", "/slow", 500)
        assert h.slowest("inst-1", 1)[0].endpoint == "/slow"

    def test_isolation(self):
        h = AppAPIDeveloperAPIEndpointLatencyHistogram()
        h.record("inst-1", "/api/a", 30)
        assert len(h.slowest("inst-2")) == 0
