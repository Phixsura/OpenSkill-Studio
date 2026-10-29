from app.services.app_api_developer_api_webhook_fan_out_manager import AppAPIDeveloperAPIWebhookFanOutManager

class TestFanOutManager:
    def test_add_target(self):
        m = AppAPIDeveloperAPIWebhookFanOutManager()
        t = m.add_target("inst-1", "t1", "https://a.com", ["push", "issue"])
        assert len(t.event_types) == 2

    def test_fan_out(self):
        m = AppAPIDeveloperAPIWebhookFanOutManager()
        m.add_target("inst-1", "t1", "https://a.com", ["push"])
        m.add_target("inst-1", "t2", "https://b.com", ["push", "issue"])
        m.add_target("inst-1", "t3", "https://c.com", ["issue"])
        r = m.fan_out("inst-1", "push")
        assert r.targets_matched == 2
        assert r.targets_delivered == 2

    def test_fan_out_with_failures(self):
        m = AppAPIDeveloperAPIWebhookFanOutManager()
        m.add_target("inst-1", "t1", "https://a.com", ["push"])
        m.add_target("inst-1", "t2", "https://b.com", ["push"])
        r = m.fan_out("inst-1", "push", {"t1": True, "t2": False})
        assert r.targets_failed == 1

    def test_toggle(self):
        m = AppAPIDeveloperAPIWebhookFanOutManager()
        m.add_target("inst-1", "t1", "https://a.com", ["push"])
        m.toggle("inst-1", "t1", False)
        r = m.fan_out("inst-1", "push")
        assert r.targets_matched == 0

    def test_isolation(self):
        m = AppAPIDeveloperAPIWebhookFanOutManager()
        m.add_target("inst-1", "t1", "https://a.com", [])
        assert len(m.list_targets("inst-2")) == 0
