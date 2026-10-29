from app.services.app_api_developer_api_key_expiry_notification import AppAPIDeveloperAPIKeyExpiryNotification

class TestExpiryNotif:
    def test_create(self):
        n = AppAPIDeveloperAPIKeyExpiryNotification()
        notif = n.create("inst-1", "n1", "k1", "alice", 14)
        assert notif.sent is False

    def test_urgent(self):
        n = AppAPIDeveloperAPIKeyExpiryNotification()
        n.create("inst-1", "n1", "k1", "alice", 3)
        n.create("inst-1", "n2", "k2", "bob", 30)
        assert len(n.urgent("inst-1", 7)) == 1

    def test_mark_sent(self):
        n = AppAPIDeveloperAPIKeyExpiryNotification()
        n.create("inst-1", "n1", "k1", "alice", 7)
        n.mark_sent("inst-1", "n1")
        assert n.pending("inst-1") == []

    def test_isolation(self):
        n = AppAPIDeveloperAPIKeyExpiryNotification()
        n.create("inst-1", "n1", "k1", "alice", 5)
        assert n.pending("inst-2") == []
