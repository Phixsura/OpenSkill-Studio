import pytest
from app.services.app_api_developer_api_access_token_manager import AppAPIDeveloperAPIAccessTokenManager

class TestTokenManager:
    def test_create_validate(self):
        m = AppAPIDeveloperAPIAccessTokenManager()
        t, raw = m.create("inst-1", "t1", "alice", "My Token", ["read", "write"])
        assert m.validate("inst-1", raw) is not None
        assert m.validate("inst-1", "bad") is None

    def test_revoke(self):
        m = AppAPIDeveloperAPIAccessTokenManager()
        _, raw = m.create("inst-1", "t1", "alice", "Token")
        m.revoke("inst-1", "t1")
        assert m.validate("inst-1", raw) is None

    def test_use_count(self):
        m = AppAPIDeveloperAPIAccessTokenManager()
        _, raw = m.create("inst-1", "t1", "alice", "Token")
        m.validate("inst-1", raw)
        m.validate("inst-1", raw)
        assert m.list_tokens("inst-1")[0].use_count == 2

    def test_isolation(self):
        m = AppAPIDeveloperAPIAccessTokenManager()
        m.create("inst-1", "t1", "alice", "Token")
        assert m.list_tokens("inst-2") == []
