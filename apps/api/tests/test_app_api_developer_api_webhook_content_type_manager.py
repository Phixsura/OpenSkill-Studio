import pytest
from app.services.app_api_developer_api_webhook_content_type_manager import AppAPIDeveloperAPIWebhookContentTypeManager

class TestContentTypeManager:
    def test_configure(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        c = m.configure("inst-1", "https://a.com", "application/json")
        assert c.content_type == "application/json"

    def test_invalid_content_type(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        with pytest.raises(ValueError):
            m.configure("inst-1", "https://a.com", "text/html")

    def test_get_content_type_header(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        m.configure("inst-1", "https://a.com", "application/xml", "iso-8859-1")
        assert m.get_content_type("inst-1", "https://a.com") == "application/xml; charset=iso-8859-1"

    def test_default_content_type(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        assert m.get_content_type("inst-1", "https://unknown.com") == "application/json; charset=utf-8"

    def test_by_content_type(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        m.configure("inst-1", "https://a.com", "application/json")
        m.configure("inst-1", "https://b.com", "application/json")
        m.configure("inst-1", "https://c.com", "application/xml")
        assert m.by_content_type("inst-1") == {"application/json": 2, "application/xml": 1}

    def test_isolation(self):
        m = AppAPIDeveloperAPIWebhookContentTypeManager()
        m.configure("inst-1", "https://a.com", "application/json")
        assert len(m.list_configs("inst-2")) == 0
