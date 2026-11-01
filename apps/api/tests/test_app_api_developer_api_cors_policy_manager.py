import pytest
from app.services.app_api_developer_api_cors_policy_manager import AppAPIDeveloperAPICORSPolicyManager

class TestCORSPolicyManager:
    def test_create(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        p = m.create("inst-1", "p1", ["https://app.example.com"], ["GET", "POST"])
        assert p.allowed_methods == ["GET", "POST"]

    def test_wildcard_with_credentials_rejected(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        with pytest.raises(ValueError, match="wildcard"):
            m.create("inst-1", "p1", ["*"], allow_credentials=True)

    def test_invalid_origin(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        with pytest.raises(ValueError, match="Invalid origin"):
            m.create("inst-1", "p1", ["javascript:alert(1)"])

    def test_check_origin(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        m.create("inst-1", "p1", ["https://app.com", "https://dev.app.com"])
        assert m.check_origin("inst-1", "p1", "https://app.com") is True
        assert m.check_origin("inst-1", "p1", "https://evil.com") is False

    def test_wildcard_allows_all(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        m.create("inst-1", "p1", ["*"])
        assert m.check_origin("inst-1", "p1", "https://anything.com") is True

    def test_isolation(self):
        m = AppAPIDeveloperAPICORSPolicyManager()
        m.create("inst-1", "p1", ["https://a.com"])
        assert len(m.list_policies("inst-2")) == 0
