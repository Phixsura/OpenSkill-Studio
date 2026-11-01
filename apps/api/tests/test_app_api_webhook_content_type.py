"""Tests for App API Webhook Content Type — configure, default, delivery."""

import pytest
from app.services.app_api_webhook_content_type import AppAPIWebhookContentType


class TestConfigure:
    def test_configure(self):
        c = AppAPIWebhookContentType()
        cfg = c.configure("inst-1", "https://a.com", "application/xml")
        assert cfg.content_type == "application/xml"

    def test_invalid(self):
        c = AppAPIWebhookContentType()
        with pytest.raises(ValueError):
            c.configure("inst-1", "https://a.com", "text/html")


class TestDefault:
    def test_default(self):
        c = AppAPIWebhookContentType()
        assert c.get_content_type("inst-1", "https://unconfigured.com") == "application/json"

    def test_override(self):
        c = AppAPIWebhookContentType()
        c.configure("inst-1", "https://a.com", "application/xml")
        assert c.get_content_type("inst-1", "https://a.com") == "application/xml"


class TestIsolation:
    def test_cross(self):
        c = AppAPIWebhookContentType()
        c.configure("inst-1", "https://a.com", "application/xml")
        assert c.get_content_type("inst-2", "https://a.com") == "application/json"
