import pytest
from app.services.app_api_developer_api_api_api_key_permission_matrix import AppAPIDeveloperAPIApiApiKeyPermissionMatrix

class TestKeyPermissionMatrix:
    def test_grant(self):
        m = AppAPIDeveloperAPIApiApiKeyPermissionMatrix()
        m.grant("inst-1", "k1", "/api/users", ["GET", "POST"])
        assert m.check("inst-1", "k1", "/api/users", "GET") is True
        assert m.check("inst-1", "k1", "/api/users", "DELETE") is False

    def test_deny(self):
        m = AppAPIDeveloperAPIApiApiKeyPermissionMatrix()
        m.grant("inst-1", "k1", "/api/admin", ["GET"])
        m.deny("inst-1", "k1", "/api/admin")
        assert m.check("inst-1", "k1", "/api/admin", "GET") is False

    def test_grant_denied_endpoint_raises(self):
        m = AppAPIDeveloperAPIApiApiKeyPermissionMatrix()
        m.deny("inst-1", "k1", "/api/secret")
        with pytest.raises(ValueError):
            m.grant("inst-1", "k1", "/api/secret", ["GET"])

    def test_unknown_key(self):
        m = AppAPIDeveloperAPIApiApiKeyPermissionMatrix()
        assert m.check("inst-1", "unknown", "/api", "GET") is False

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiApiKeyPermissionMatrix()
        m.grant("inst-1", "k1", "/api", ["GET"])
        assert len(m.all_keys("inst-2")) == 0
