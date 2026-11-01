from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_access_token_manager import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager

class TestApiAccessTokenManager:
    def test_issue_and_validate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager()
        result = svc.issue("inst-1", "c1", ["read", "write"])
        at = svc.validate("inst-1", result["token_id"], result["access_token"])
        assert at is not None
        assert at.consumer_id == "c1"
        assert "read" in at.scopes

    def test_wrong_token_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager()
        result = svc.issue("inst-1", "c1", ["read"])
        assert svc.validate("inst-1", result["token_id"], "wrong-token") is None

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager()
        result = svc.issue("inst-1", "c1", ["read"])
        svc.revoke("inst-1", result["token_id"])
        assert svc.validate("inst-1", result["token_id"], result["access_token"]) is None

    def test_no_plaintext_stored(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager()
        result = svc.issue("inst-1", "c1", ["read"])
        at = svc._access[("inst-1", result["token_id"])]
        assert result["access_token"] not in at.token_hash

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiAccessTokenManager()
        svc.issue("inst-1", "c1", ["read"])
        assert svc.active_token_count("inst-2") == 0
