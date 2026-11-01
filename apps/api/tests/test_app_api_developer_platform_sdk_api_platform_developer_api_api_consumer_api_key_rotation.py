from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_key_rotation import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation

class TestConsumerApiKeyRotation:
    def test_issue_and_validate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation()
        result = svc.issue_key("inst-1", "c1")
        v = svc.validate("inst-1", "c1", result["key"])
        assert v["valid"] is True and v["is_current"] is True

    def test_rotation_both_valid_during_grace(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation()
        k1 = svc.issue_key("inst-1", "c1", grace_period_s=9999)
        k2 = svc.issue_key("inst-1", "c1", grace_period_s=9999)
        assert svc.validate("inst-1", "c1", k1["key"])["valid"] is True
        assert svc.validate("inst-1", "c1", k2["key"])["valid"] is True
        assert svc.validate("inst-1", "c1", k2["key"])["is_current"] is True

    def test_wrong_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation()
        svc.issue_key("inst-1", "c1")
        assert svc.validate("inst-1", "c1", "wrong")["valid"] is False

    def test_revoke_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation()
        k = svc.issue_key("inst-1", "c1")
        count = svc.revoke_all("inst-1", "c1")
        assert count == 1
        assert svc.validate("inst-1", "c1", k["key"])["valid"] is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation()
        svc.issue_key("inst-1", "c1")
        assert svc.get_rotation("inst-2", "c1") is None
