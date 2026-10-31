import pytest
from app.services.app_api_webhook_event_filter import AppAPIWebhookEventFilter

class TestFilter:
    def test_eq_match(self):
        f = AppAPIWebhookEventFilter()
        f.add_filter("inst-1", "f1", "push", "data.branch", "eq", "main")
        assert f.matches("inst-1", "push", {"data": {"branch": "main"}}) is True
        assert f.matches("inst-1", "push", {"data": {"branch": "dev"}}) is False

    def test_contains(self):
        f = AppAPIWebhookEventFilter()
        f.add_filter("inst-1", "f1", "push", "data.message", "contains", "fix")
        assert f.matches("inst-1", "push", {"data": {"message": "bug fix #123"}}) is True

    def test_no_filters(self):
        f = AppAPIWebhookEventFilter()
        assert f.matches("inst-1", "push", {}) is True

    def test_invalid_op(self):
        f = AppAPIWebhookEventFilter()
        with pytest.raises(ValueError):
            f.add_filter("inst-1", "f1", "push", "x", "like", "y")

    def test_isolation(self):
        f = AppAPIWebhookEventFilter()
        f.add_filter("inst-1", "f1", "push", "x", "eq", "y")
        assert f.matches("inst-2", "push", {"x": "z"}) is True
