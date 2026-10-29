import pytest
from app.services.app_api_developer_marketplace import AppAPIDeveloperMarketplace

class TestMarketplace:
    def test_create_publish(self):
        m = AppAPIDeveloperMarketplace()
        l = m.create("inst-1", "l1", "Auth Plugin", "OAuth integration", "auth")
        m.publish("inst-1", "l1")
        assert m.top_listings("inst-1")[0].published is True

    def test_install_count(self):
        m = AppAPIDeveloperMarketplace()
        m.create("inst-1", "l1", "Plugin", "Desc", "tools")
        m.publish("inst-1", "l1")
        m.record_install("inst-1", "l1")
        m.record_install("inst-1", "l1")
        assert m.list_all("inst-1")[0].install_count == 2

    def test_by_category(self):
        m = AppAPIDeveloperMarketplace()
        m.create("inst-1", "l1", "A", "D", "auth")
        m.create("inst-1", "l2", "B", "D", "tools")
        m.publish("inst-1", "l1")
        m.publish("inst-1", "l2")
        assert len(m.by_category("inst-1", "auth")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperMarketplace()
        m.create("inst-1", "l1", "A", "D", "auth")
        assert m.list_all("inst-2") == []
