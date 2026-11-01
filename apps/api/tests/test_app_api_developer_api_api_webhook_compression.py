import pytest
from app.services.app_api_developer_api_api_webhook_compression import AppAPIDeveloperAPIApiWebhookCompression

class TestWebhookCompression:
    def test_compress(self):
        c = AppAPIDeveloperAPIApiWebhookCompression()
        r = c.compress("inst-1", "a" * 10000)
        assert r.compressed_bytes < r.original_bytes
        assert r.savings_pct > 0

    def test_invalid_algorithm(self):
        c = AppAPIDeveloperAPIApiWebhookCompression()
        with pytest.raises(ValueError):
            c.compress("inst-1", "data", "brotli")

    def test_stats(self):
        c = AppAPIDeveloperAPIApiWebhookCompression()
        c.compress("inst-1", "x" * 5000)
        c.compress("inst-1", "y" * 3000)
        s = c.stats("inst-1")
        assert s["count"] == 2
        assert s["avg_savings_pct"] > 0

    def test_should_compress(self):
        c = AppAPIDeveloperAPIApiWebhookCompression()
        assert c.should_compress("small") is False
        assert c.should_compress("x" * 2000) is True

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiWebhookCompression()
        c.compress("inst-1", "data" * 100)
        assert c.stats("inst-2")["count"] == 0
