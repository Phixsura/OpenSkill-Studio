import pytest
from app.services.app_api_developer_notification import AppAPIDeveloperNotification

class TestNotification:
    def test_send(self):
        n = AppAPIDeveloperNotification()
        notif = n.send("inst-1", "n1", "alice", "API Update", "New version available")
        assert notif.read is False

    def test_mark_read(self):
        n = AppAPIDeveloperNotification()
        n.send("inst-1", "n1", "alice", "Update", "Body")
        n.mark_read("inst-1", "n1")
        assert n.unread("inst-1", "alice") == []

    def test_unread_count(self):
        n = AppAPIDeveloperNotification()
        n.send("inst-1", "n1", "alice", "A", "B")
        n.send("inst-1", "n2", "alice", "C", "D")
        n.mark_read("inst-1", "n1")
        assert len(n.unread("inst-1", "alice")) == 1

    def test_isolation(self):
        n = AppAPIDeveloperNotification()
        n.send("inst-1", "n1", "alice", "A", "B")
        assert n.count("inst-2") == 0
