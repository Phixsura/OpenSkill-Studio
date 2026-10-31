import pytest
from app.services.app_api_developer_community import AppAPIDeveloperCommunity

class TestCommunity:
    def test_create(self):
        c = AppAPIDeveloperCommunity()
        d = c.create_discussion("inst-1", "d1", "How to authenticate?", "alice")
        assert d.reply_count == 0

    def test_reply_resolve(self):
        c = AppAPIDeveloperCommunity()
        c.create_discussion("inst-1", "d1", "Question", "alice")
        c.add_reply("inst-1", "d1")
        c.resolve("inst-1", "d1")
        assert c.open_discussions("inst-1") == []

    def test_open(self):
        c = AppAPIDeveloperCommunity()
        c.create_discussion("inst-1", "d1", "Q1", "a")
        c.create_discussion("inst-1", "d2", "Q2", "b")
        c.resolve("inst-1", "d1")
        assert len(c.open_discussions("inst-1")) == 1

    def test_isolation(self):
        c = AppAPIDeveloperCommunity()
        c.create_discussion("inst-1", "d1", "Q", "a")
        assert c.list_discussions("inst-2") == []
