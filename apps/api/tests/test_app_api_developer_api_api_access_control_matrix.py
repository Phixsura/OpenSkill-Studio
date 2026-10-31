import pytest
from app.services.app_api_developer_api_api_access_control_matrix import AppAPIDeveloperAPIApiAccessControlMatrix

class TestAccessControlMatrix:
    def test_allowed(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        m.set_rule("inst-1", "/api/admin", "GET", allowed_roles=["admin"])
        assert m.check_access("inst-1", "/api/admin", "GET", "admin") is True
        assert m.check_access("inst-1", "/api/admin", "GET", "user") is False

    def test_public(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        m.set_rule("inst-1", "/api/health", "GET", public=True)
        assert m.check_access("inst-1", "/api/health", "GET", "anonymous") is True

    def test_denied(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        m.set_rule("inst-1", "/api/data", "GET", allowed_roles=["admin", "viewer"], denied_roles=["blocked"])
        assert m.check_access("inst-1", "/api/data", "GET", "blocked") is False

    def test_conflict_rejected(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        with pytest.raises(ValueError):
            m.set_rule("inst-1", "/api/data", "GET", allowed_roles=["admin"], denied_roles=["admin"])

    def test_default_deny(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        assert m.check_access("inst-1", "/unknown", "GET", "admin") is False

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiAccessControlMatrix()
        m.set_rule("inst-1", "/api/a", "GET", allowed_roles=["admin"])
        assert len(m.all_rules("inst-2")) == 0
