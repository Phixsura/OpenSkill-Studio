import pytest
from app.services.app_api_webhook_priority import AppAPIWebhookPriority

class TestPriority:
    def test_set(self):
        p = AppAPIWebhookPriority()
        ep = p.set_priority("inst-1", "security.alert", 5)
        assert ep.priority == 5

    def test_invalid(self):
        p = AppAPIWebhookPriority()
        with pytest.raises(ValueError):
            p.set_priority("inst-1", "x", 0)

    def test_default(self):
        p = AppAPIWebhookPriority()
        assert p.get_priority("inst-1", "unknown") == 3

    def test_sorted(self):
        p = AppAPIWebhookPriority()
        p.set_priority("inst-1", "low", 1)
        p.set_priority("inst-1", "high", 5)
        p.set_priority("inst-1", "mid", 3)
        s = p.sorted_by_priority("inst-1")
        assert s[0].event_type == "high"

    def test_isolation(self):
        p = AppAPIWebhookPriority()
        p.set_priority("inst-1", "x", 5)
        assert p.list_priorities("inst-2") == []
