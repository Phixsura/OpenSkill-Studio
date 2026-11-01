import pytest
from app.services.app_api_developer_api_api_developer_api_webhook_header_manager import AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager

class TestHeaderManager:
    def test_set_headers(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        c = m.set_headers("inst-1", "https://a.com", {"X-Custom": "value", "X-Source": "api"})
        assert len(c.headers) == 2

    def test_forbidden_header(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        with pytest.raises(ValueError, match="Forbidden"):
            m.set_headers("inst-1", "https://a.com", {"Host": "evil.com"})

    def test_invalid_name(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        with pytest.raises(ValueError, match="Invalid"):
            m.add_header("inst-1", "https://a.com", "Bad Header Name", "value")

    def test_add_and_remove(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        m.add_header("inst-1", "https://a.com", "X-Custom", "v1")
        m.add_header("inst-1", "https://a.com", "X-Source", "api")
        m.remove_header("inst-1", "https://a.com", "X-Custom")
        headers = m.get_headers("inst-1", "https://a.com")
        assert "X-Custom" not in headers
        assert "X-Source" in headers

    def test_empty_default(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        assert m.get_headers("inst-1", "https://unknown.com") == {}

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager()
        m.set_headers("inst-1", "https://a.com", {"X-A": "1"})
        assert len(m.all_configs("inst-2")) == 0
