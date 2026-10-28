"""Tests for App API Webhook Retry Config — strategy, delay calculation."""

import pytest
from app.services.app_api_webhook_retry_config import AppAPIWebhookRetryConfig


class TestConfig:
    def test_set(self):
        r = AppAPIWebhookRetryConfig()
        c = r.set_config("inst-1", "c1", "https://a.com", "exponential", 5, 1000)
        assert c.strategy == "exponential"

    def test_invalid_strategy(self):
        r = AppAPIWebhookRetryConfig()
        with pytest.raises(ValueError):
            r.set_config("inst-1", "c1", "https://a.com", "random")


class TestDelay:
    def test_fixed(self):
        r = AppAPIWebhookRetryConfig()
        c = r.set_config("inst-1", "c1", "https://a.com", "fixed", initial_delay_ms=2000)
        assert c.delay_for_attempt(1) == 2000
        assert c.delay_for_attempt(3) == 2000

    def test_exponential(self):
        r = AppAPIWebhookRetryConfig()
        c = r.set_config("inst-1", "c1", "https://a.com", "exponential", initial_delay_ms=1000, max_delay_ms=10000)
        assert c.delay_for_attempt(1) == 1000
        assert c.delay_for_attempt(2) == 2000
        assert c.delay_for_attempt(4) == 8000
        assert c.delay_for_attempt(5) == 10000  # capped


class TestLookup:
    def test_find(self):
        r = AppAPIWebhookRetryConfig()
        r.set_config("inst-1", "c1", "https://a.com")
        assert r.get_for_destination("inst-1", "https://a.com") is not None
        assert r.get_for_destination("inst-1", "https://b.com") is None


class TestIsolation:
    def test_cross(self):
        r = AppAPIWebhookRetryConfig()
        r.set_config("inst-1", "c1", "https://a.com")
        assert r.list_configs("inst-2") == []
