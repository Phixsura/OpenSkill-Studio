import pytest
from app.services.app_api_webhook_destination_group import AppAPIWebhookDestinationGroup

class TestGroup:
    def test_create(self):
        g = AppAPIWebhookDestinationGroup()
        grp = g.create("inst-1", "g1", "Production", ["https://a.com", "https://b.com"])
        assert len(grp.destinations) == 2

    def test_add_remove(self):
        g = AppAPIWebhookDestinationGroup()
        g.create("inst-1", "g1", "Prod", ["https://a.com"])
        g.add_destination("inst-1", "g1", "https://b.com")
        g.remove_destination("inst-1", "g1", "https://a.com")
        assert g.list_groups("inst-1")[0].destinations == ["https://b.com"]

    def test_toggle(self):
        g = AppAPIWebhookDestinationGroup()
        g.create("inst-1", "g1", "Prod", ["https://a.com"])
        g.toggle("inst-1", "g1", False)
        assert g.active_groups("inst-1") == []

    def test_isolation(self):
        g = AppAPIWebhookDestinationGroup()
        g.create("inst-1", "g1", "Prod", ["https://a.com"])
        assert g.list_groups("inst-2") == []
