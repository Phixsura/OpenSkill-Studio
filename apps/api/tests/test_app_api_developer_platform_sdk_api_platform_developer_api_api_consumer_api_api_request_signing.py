import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_signing import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning

class TestRequestSigning:
    def test_sign_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning()
        svc.configure("inst-1", "c1", "a-very-secure-signing-key-1234")
        result = svc.sign("inst-1", "c1", "POST", "/api/orders", {"content-type": "application/json"}, '{"item":"a"}')
        assert result.signature
        assert svc.verify("inst-1", "c1", "POST", "/api/orders", {"content-type": "application/json"}, '{"item":"a"}', result.signature) is True

    def test_tampered_body_fails(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning()
        svc.configure("inst-1", "c1", "a-very-secure-signing-key-1234")
        result = svc.sign("inst-1", "c1", "POST", "/api", {}, '{"original":true}')
        assert svc.verify("inst-1", "c1", "POST", "/api", {}, '{"tampered":true}', result.signature) is False

    def test_short_secret_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning()
        with pytest.raises(ValueError, match="at least 16"):
            svc.configure("inst-1", "c1", "short")

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning()
        with pytest.raises(ValueError, match="Invalid algorithm"):
            svc.configure("inst-1", "c1", "a-very-secure-signing-key-1234", algorithm="md5")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSigning()
        svc.configure("inst-1", "c1", "a-very-secure-signing-key-1234")
        assert len(svc.list_configs("inst-2")) == 0
