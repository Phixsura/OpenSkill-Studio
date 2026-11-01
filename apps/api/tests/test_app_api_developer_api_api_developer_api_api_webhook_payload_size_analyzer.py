from app.services.app_api_developer_api_api_developer_api_api_webhook_payload_size_analyzer import AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer

class TestPayloadSizeAnalyzer:
    def test_record(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer()
        s = a.record("inst-1", "https://a.com", 1024)
        assert s.avg_bytes == 1024.0

    def test_min_max(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer()
        a.record("inst-1", "https://a.com", 100)
        a.record("inst-1", "https://a.com", 500)
        a.record("inst-1", "https://a.com", 200)
        s = a.get("inst-1", "https://a.com")
        assert s.min_bytes == 100
        assert s.max_bytes == 500

    def test_oversized(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer(max_payload_bytes=1000)
        a.record("inst-1", "https://a.com", 500)
        a.record("inst-1", "https://a.com", 2000)
        assert len(a.oversized_destinations("inst-1")) == 1

    def test_bandwidth(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer()
        a.record("inst-1", "https://a.com", 1000)
        a.record("inst-1", "https://b.com", 2000)
        assert a.total_bandwidth("inst-1") == 3000

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer()
        a.record("inst-1", "https://a.com", 1000)
        assert a.total_bandwidth("inst-2") == 0
