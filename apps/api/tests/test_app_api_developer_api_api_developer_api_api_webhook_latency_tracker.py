from app.services.app_api_developer_api_api_developer_api_api_webhook_latency_tracker import AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker

class TestWebhookLatencyTracker:
    def test_record(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker()
        s = t.record("inst-1", "https://a.com", 50.0)
        assert s.avg_ms == 50.0

    def test_percentiles(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker()
        for i in range(100): t.record("inst-1", "https://a.com", float(i + 1))
        s = t.get("inst-1", "https://a.com")
        assert s.p50_ms == 51.0
        assert s.p99_ms == 100.0

    def test_slowest(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker()
        for _ in range(10): t.record("inst-1", "https://fast.com", 10.0)
        for _ in range(10): t.record("inst-1", "https://slow.com", 500.0)
        assert t.slowest("inst-1", 1)[0].destination == "https://slow.com"

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookLatencyTracker()
        t.record("inst-1", "https://a.com", 50.0)
        assert len(t.all_destinations("inst-2")) == 0
