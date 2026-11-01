from app.services.app_api_developer_api_api_developer_api_api_webhook_destination_health import AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth

class TestDestinationHealth:
    def test_healthy(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        for _ in range(10): h.record("inst-1", "https://a.com", True, 50)
        d = h.get("inst-1", "https://a.com")
        assert d.status == "healthy"
        assert d.success_rate == 100.0

    def test_degraded(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        h.record("inst-1", "https://a.com", True, 50)
        for _ in range(3): h.record("inst-1", "https://a.com", False, 100)
        assert h.get("inst-1", "https://a.com").status == "degraded"

    def test_down(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        for _ in range(10): h.record("inst-1", "https://a.com", False, 100)
        assert h.get("inst-1", "https://a.com").status == "down"

    def test_recovery(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        for _ in range(5): h.record("inst-1", "https://a.com", False, 100)
        h.record("inst-1", "https://a.com", True, 50)
        assert h.get("inst-1", "https://a.com").consecutive_failures == 0

    def test_unhealthy_list(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        for _ in range(10): h.record("inst-1", "https://a.com", True, 50)
        for _ in range(10): h.record("inst-1", "https://b.com", False, 100)
        assert len(h.unhealthy("inst-1")) == 1

    def test_isolation(self):
        h = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth()
        h.record("inst-1", "https://a.com", True, 50)
        assert len(h.all_destinations("inst-2")) == 0
