import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_token_exchange import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange

class TestTokenExchange:
    def test_generate_and_exchange(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange()
        result = svc.generate_code("inst-1", "c1", ["read", "write"])
        tokens = svc.exchange("inst-1", result["code_id"], result["code"])
        assert tokens.access_token and tokens.refresh_token
        assert "read" in tokens.scopes

    def test_code_reuse_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange()
        result = svc.generate_code("inst-1", "c1", ["read"])
        svc.exchange("inst-1", result["code_id"], result["code"])
        with pytest.raises(ValueError, match="already used"):
            svc.exchange("inst-1", result["code_id"], result["code"])

    def test_wrong_code(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange()
        result = svc.generate_code("inst-1", "c1", ["read"])
        with pytest.raises(ValueError, match="Invalid code"):
            svc.exchange("inst-1", result["code_id"], "wrong-code")

    def test_redirect_mismatch(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange()
        result = svc.generate_code("inst-1", "c1", ["read"], redirect_uri="https://app.com/cb")
        with pytest.raises(ValueError, match="Redirect"):
            svc.exchange("inst-1", result["code_id"], result["code"], redirect_uri="https://evil.com/cb")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTokenExchange()
        svc.generate_code("inst-1", "c1", ["read"])
        assert svc.pending_codes("inst-2") == 0
