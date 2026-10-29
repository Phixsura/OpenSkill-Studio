from app.services.app_api_developer_api_api_webhook_event_filter import AppAPIDeveloperAPIApiWebhookEventFilter

class TestWebhookEventFilter:
    def test_include(self):
        f = AppAPIDeveloperAPIApiWebhookEventFilter()
        f.create("inst-1", "f1", "https://a.com", include_events=["push", "issue"])
        assert f.should_deliver("inst-1", "f1", "push", {}) is True
        assert f.should_deliver("inst-1", "f1", "deploy", {}) is False

    def test_exclude(self):
        f = AppAPIDeveloperAPIApiWebhookEventFilter()
        f.create("inst-1", "f1", "https://a.com", exclude_events=["ping"])
        assert f.should_deliver("inst-1", "f1", "push", {}) is True
        assert f.should_deliver("inst-1", "f1", "ping", {}) is False

    def test_field_filter(self):
        f = AppAPIDeveloperAPIApiWebhookEventFilter()
        f.create("inst-1", "f1", "https://a.com", field_filters={"action": "^(opened|closed)$"})
        assert f.should_deliver("inst-1", "f1", "issue", {"action": "opened"}) is True
        assert f.should_deliver("inst-1", "f1", "issue", {"action": "edited"}) is False

    def test_stats(self):
        f = AppAPIDeveloperAPIApiWebhookEventFilter()
        f.create("inst-1", "f1", "https://a.com", include_events=["push"])
        f.should_deliver("inst-1", "f1", "push", {})
        f.should_deliver("inst-1", "f1", "issue", {})
        s = f.stats("inst-1", "f1")
        assert s == {"matched": 1, "dropped": 1}

    def test_isolation(self):
        f = AppAPIDeveloperAPIApiWebhookEventFilter()
        f.create("inst-1", "f1", "https://a.com")
        assert len(f.list_filters("inst-2")) == 0
