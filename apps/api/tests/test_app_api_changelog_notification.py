import pytest
from app.services.app_api_changelog_notification import AppAPIChangelogNotification

class TestNotification:
    def test_send(self):
        n = AppAPIChangelogNotification()
        nr = n.send("inst-1", "n1", "v2.0", "email", 100)
        assert nr.recipient_count == 100

    def test_delivery(self):
        n = AppAPIChangelogNotification()
        n.send("inst-1", "n1", "v2.0", "slack", 50)
        nr = n.record_delivery("inst-1", "n1", 48, 2)
        assert nr.delivered == 48

    def test_invalid_channel(self):
        n = AppAPIChangelogNotification()
        with pytest.raises(ValueError):
            n.send("inst-1", "n1", "v1", "sms", 10)

    def test_isolation(self):
        n = AppAPIChangelogNotification()
        n.send("inst-1", "n1", "v1", "email", 10)
        assert n.count("inst-2") == 0
