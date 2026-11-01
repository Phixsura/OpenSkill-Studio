import pytest
from app.services.app_api_developer_platform_sdk_api_key_audit_trail import AppAPIDeveloperPlatformSDKApiKeyAuditTrail

class TestApiKeyAuditTrail:
    def test_log(self):
        a = AppAPIDeveloperPlatformSDKApiKeyAuditTrail()
        e = a.log("inst-1", "e1", "k1", "created", "admin@acme.com", "1.2.3.4")
        assert e.action == "created"

    def test_invalid_action(self):
        a = AppAPIDeveloperPlatformSDKApiKeyAuditTrail()
        with pytest.raises(ValueError):
            a.log("inst-1", "e1", "k1", "hacked", "admin")

    def test_by_key(self):
        a = AppAPIDeveloperPlatformSDKApiKeyAuditTrail()
        a.log("inst-1", "e1", "k1", "created", "admin")
        a.log("inst-1", "e2", "k2", "created", "admin")
        a.log("inst-1", "e3", "k1", "rotated", "admin")
        assert len(a.by_key("inst-1", "k1")) == 2

    def test_action_counts(self):
        a = AppAPIDeveloperPlatformSDKApiKeyAuditTrail()
        a.log("inst-1", "e1", "k1", "created", "a")
        a.log("inst-1", "e2", "k2", "created", "a")
        a.log("inst-1", "e3", "k1", "revoked", "a")
        assert a.action_counts("inst-1") == {"created": 2, "revoked": 1}

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiKeyAuditTrail()
        a.log("inst-1", "e1", "k1", "created", "admin")
        assert len(a.recent("inst-2")) == 0
