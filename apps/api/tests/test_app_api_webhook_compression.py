import pytest
from app.services.app_api_webhook_compression import AppAPIWebhookCompression

class TestCompression:
    def test_configure(self):
        c = AppAPIWebhookCompression()
        cfg = c.configure("inst-1", "https://a.com", "gzip")
        assert cfg.algorithm == "gzip"

    def test_invalid_algo(self):
        c = AppAPIWebhookCompression()
        with pytest.raises(ValueError):
            c.configure("inst-1", "https://a.com", "lz4")

    def test_savings(self):
        c = AppAPIWebhookCompression()
        c.configure("inst-1", "https://a.com", "gzip")
        c.record_savings("inst-1", "https://a.com", 500)
        assert c.get_config("inst-1", "https://a.com").bytes_saved == 500

    def test_isolation(self):
        c = AppAPIWebhookCompression()
        c.configure("inst-1", "https://a.com")
        assert c.list_configs("inst-2") == []
