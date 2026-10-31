import pytest
from app.services.app_api_developer_api_notification_center import AppAPIDeveloperAPINotificationCenter

class TestCenter:
    def test_send(self):
        c = AppAPIDeveloperAPINotificationCenter()
        n = c.send("inst-1", "n1", "New Version", "v3.0 released", "changelog")
        assert n.read is False

    def test_unread(self):
        c = AppAPIDeveloperAPINotificationCenter()
        c.send("inst-1", "n1", "A", "B", "system")
        c.send("inst-1", "n2", "C", "D", "incident")
        c.mark_read("inst-1", "n1")
        assert c.unread_count("inst-1") == 1

    def test_category(self):
        c = AppAPIDeveloperAPINotificationCenter()
        c.send("inst-1", "n1", "A", "B", "security")
        c.send("inst-1", "n2", "C", "D", "billing")
        assert len(c.by_category("inst-1", "security")) == 1

    def test_invalid_category(self):
        c = AppAPIDeveloperAPINotificationCenter()
        with pytest.raises(ValueError):
            c.send("inst-1", "n1", "A", "B", "marketing")
