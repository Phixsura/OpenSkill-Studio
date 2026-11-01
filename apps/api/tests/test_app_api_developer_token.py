import pytest
from app.services.app_api_developer_token import AppAPIDeveloperToken

class TestToken:
    def test_create_validate(self):
        t = AppAPIDeveloperToken()
        token, raw = t.create("inst-1", "t1", "alice", "My Token", ["read"])
        assert t.validate("inst-1", raw) is not None
        assert t.validate("inst-1", "bad") is None

    def test_revoke(self):
        t = AppAPIDeveloperToken()
        _, raw = t.create("inst-1", "t1", "alice", "Token")
        t.revoke("inst-1", "t1")
        assert t.validate("inst-1", raw) is None

    def test_list_by_dev(self):
        t = AppAPIDeveloperToken()
        t.create("inst-1", "t1", "alice", "A")
        t.create("inst-1", "t2", "bob", "B")
        assert len(t.list_tokens("inst-1", "alice")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperToken()
        t.create("inst-1", "t1", "alice", "A")
        assert t.list_tokens("inst-2") == []
