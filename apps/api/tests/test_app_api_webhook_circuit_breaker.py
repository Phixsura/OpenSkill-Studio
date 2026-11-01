"""Tests for App API Webhook Circuit Breaker — transitions."""

from app.services.app_api_webhook_circuit_breaker import AppAPIWebhookCircuitBreaker, CBState


class TestTransitions:
    def test_opens_on_threshold(self):
        cb = AppAPIWebhookCircuitBreaker(failure_threshold=3, cooldown_seconds=60)
        for _ in range(3):
            cb.record_failure("inst-1", "https://a.com")
        assert not cb.should_allow("inst-1", "https://a.com")

    def test_half_open_on_cooldown(self):
        cb = AppAPIWebhookCircuitBreaker(failure_threshold=1, cooldown_seconds=0)
        cb.record_failure("inst-1", "https://a.com")
        assert cb.should_allow("inst-1", "https://a.com")  # cooldown=0

    def test_success_closes(self):
        cb = AppAPIWebhookCircuitBreaker(failure_threshold=1, cooldown_seconds=0)
        cb.record_failure("inst-1", "https://a.com")
        cb.should_allow("inst-1", "https://a.com")  # half_open
        cb.record_success("inst-1", "https://a.com")
        b = cb._breakers[("inst-1", "https://a.com")]
        assert b.state == CBState.CLOSED

    def test_default_allows(self):
        cb = AppAPIWebhookCircuitBreaker()
        assert cb.should_allow("inst-1", "https://new.com") is True


class TestIsolation:
    def test_cross(self):
        cb = AppAPIWebhookCircuitBreaker(failure_threshold=1)
        cb.record_failure("inst-1", "https://a.com")
        assert cb.should_allow("inst-2", "https://a.com") is True
