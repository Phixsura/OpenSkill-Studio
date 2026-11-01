"""Tests for App API Webhook Header — set, get, mask."""

from app.services.app_api_webhook_header import AppAPIWebhookHeader

HEADERS = [
    {"name": "X-Custom", "value": "public-value"},
    {"name": "Authorization", "value": "Bearer secret-token-123", "secret": True},
]


class TestSet:
    def test_set(self):
        h = AppAPIWebhookHeader()
        config = h.set_headers("inst-1", "https://a.com", HEADERS)
        assert len(config.headers) == 2


class TestGet:
    def test_masked(self):
        h = AppAPIWebhookHeader()
        h.set_headers("inst-1", "https://a.com", HEADERS)
        headers = h.get_headers("inst-1", "https://a.com", mask=True)
        auth = [x for x in headers if x["name"] == "Authorization"][0]
        assert "secret-token" not in auth["value"]
        assert auth["value"].startswith("Be")

    def test_unmasked(self):
        h = AppAPIWebhookHeader()
        h.set_headers("inst-1", "https://a.com", HEADERS)
        headers = h.get_headers("inst-1", "https://a.com", mask=False)
        auth = [x for x in headers if x["name"] == "Authorization"][0]
        assert auth["value"] == "Bearer secret-token-123"

    def test_no_config(self):
        h = AppAPIWebhookHeader()
        assert h.get_headers("inst-1", "https://missing.com") == []


class TestIsolation:
    def test_cross(self):
        h = AppAPIWebhookHeader()
        h.set_headers("inst-1", "https://a.com", HEADERS)
        assert h.list_destinations("inst-2") == []
