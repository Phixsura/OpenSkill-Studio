import pytest
from app.services.app_api_developer_api_api_token_scope_manager import AppAPIDeveloperAPIApiTokenScopeManager

class TestTokenScopeManager:
    def test_create(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        t = m.create("inst-1", "t1", "CI Token", ["read", "webhooks:read"])
        assert "read" in t.scopes

    def test_invalid_scope(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        with pytest.raises(ValueError, match="Invalid scopes"):
            m.create("inst-1", "t1", "Bad", ["not_real"])

    def test_check_allowed(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        m.create("inst-1", "t1", "Token", ["read", "users:read"])
        assert m.check("inst-1", "t1", "read") is True
        assert m.check("inst-1", "t1", "write") is False

    def test_admin_grants_all(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        m.create("inst-1", "t1", "Admin", ["admin"])
        assert m.check("inst-1", "t1", "billing:write") is True

    def test_revoked_denies(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        m.create("inst-1", "t1", "Token", ["read"])
        m.revoke("inst-1", "t1")
        assert m.check("inst-1", "t1", "read") is False

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiTokenScopeManager()
        m.create("inst-1", "t1", "Token", ["read"])
        assert len(m.list_tokens("inst-2")) == 0
