from app.services.app_api_webhook_status import AppAPIWebhookStatus

class TestStatus:
    def test_healthy(self):
        s = AppAPIWebhookStatus()
        ds = s.record("inst-1", "https://a.com", True)
        assert ds.status == "healthy"

    def test_degraded(self):
        s = AppAPIWebhookStatus()
        s.record("inst-1", "https://a.com", False)
        assert s.get_status("inst-1", "https://a.com").status == "degraded"

    def test_down(self):
        s = AppAPIWebhookStatus()
        for _ in range(3): s.record("inst-1", "https://a.com", False)
        assert s.get_status("inst-1", "https://a.com").status == "down"

    def test_recovery(self):
        s = AppAPIWebhookStatus()
        for _ in range(3): s.record("inst-1", "https://a.com", False)
        s.record("inst-1", "https://a.com", True)
        assert s.get_status("inst-1", "https://a.com").status == "healthy"

    def test_isolation(self):
        s = AppAPIWebhookStatus()
        s.record("inst-1", "https://a.com", False)
        assert s.list_all("inst-2") == []
