import pytest
from app.services.app_api_developer_api_api_developer_api_api_webhook_circuit_breaker_config import AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig

class TestCircuitBreakerConfig:
    def test_configure(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig()
        cfg = c.configure("inst-1", "https://a.com", 5, 60)
        assert cfg.failure_threshold == 5

    def test_success_threshold_guard(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig()
        with pytest.raises(ValueError, match="success_threshold"):
            c.configure("inst-1", "https://a.com", 5, 60, half_open_max_requests=3, success_threshold=5)

    def test_toggle(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig()
        c.configure("inst-1", "https://a.com", 5, 60)
        c.toggle("inst-1", "https://a.com", False)
        assert len(c.enabled_configs("inst-1")) == 0

    def test_get(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig()
        c.configure("inst-1", "https://a.com", 3, 30)
        cfg = c.get("inst-1", "https://a.com")
        assert cfg.recovery_timeout_seconds == 30

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig()
        c.configure("inst-1", "https://a.com", 5, 60)
        assert len(c.all_configs("inst-2")) == 0
