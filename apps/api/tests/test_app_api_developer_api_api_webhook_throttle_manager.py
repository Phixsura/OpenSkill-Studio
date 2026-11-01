import pytest
from app.services.app_api_developer_api_api_webhook_throttle_manager import AppAPIDeveloperAPIApiWebhookThrottleManager

class TestThrottleManager:
    def test_configure(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        c = t.configure("inst-1", "https://a.com", 10, 100)
        assert c.max_per_second == 10

    def test_minute_less_than_second_rejected(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        with pytest.raises(ValueError):
            t.configure("inst-1", "https://a.com", 100, 10)

    def test_allow_within_limit(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        t.configure("inst-1", "https://a.com", 5, 100)
        for _ in range(5):
            assert t.try_deliver("inst-1", "https://a.com") is True

    def test_throttle_per_second(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        t.configure("inst-1", "https://a.com", 2, 100)
        t.try_deliver("inst-1", "https://a.com")
        t.try_deliver("inst-1", "https://a.com")
        assert t.try_deliver("inst-1", "https://a.com") is False

    def test_no_config_allows(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        assert t.try_deliver("inst-1", "https://unknown.com") is True

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiWebhookThrottleManager()
        t.configure("inst-1", "https://a.com", 10, 100)
        assert len(t.all_configs("inst-2")) == 0
