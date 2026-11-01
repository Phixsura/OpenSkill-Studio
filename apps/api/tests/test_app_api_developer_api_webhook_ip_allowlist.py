import pytest
from app.services.app_api_developer_api_webhook_ip_allowlist import AppAPIDeveloperAPIWebhookIPAllowlist

class TestIPAllowlist:
    def test_create(self):
        a = AppAPIDeveloperAPIWebhookIPAllowlist()
        al = a.create("inst-1", "al1", ["192.168.1.0/24", "10.0.0.1"])
        assert len(al.entries) == 2

    def test_invalid_cidr(self):
        a = AppAPIDeveloperAPIWebhookIPAllowlist()
        with pytest.raises(ValueError):
            a.create("inst-1", "al1", ["not-an-ip"])

    def test_check_allowed(self):
        a = AppAPIDeveloperAPIWebhookIPAllowlist()
        a.create("inst-1", "al1", ["192.168.1.0/24"])
        assert a.check("inst-1", "al1", "192.168.1.50") is True
        assert a.check("inst-1", "al1", "10.0.0.1") is False

    def test_stats(self):
        a = AppAPIDeveloperAPIWebhookIPAllowlist()
        a.create("inst-1", "al1", ["10.0.0.0/8"])
        a.check("inst-1", "al1", "10.1.2.3")
        a.check("inst-1", "al1", "192.168.1.1")
        s = a.stats("inst-1", "al1")
        assert s == {"allowed": 1, "blocked": 1, "entries": 1}

    def test_isolation(self):
        a = AppAPIDeveloperAPIWebhookIPAllowlist()
        a.create("inst-1", "al1", ["10.0.0.0/8"])
        with pytest.raises(KeyError):
            a.check("inst-2", "al1", "10.0.0.1")
