import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_request_signing import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning, SigningConfig,
)

class TestConsumerApiRequestSigning:
    def test_sign_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        svc.configure("inst-1", SigningConfig(consumer_id="c1"), secret="a" * 32)
        signed = svc.sign("inst-1", "c1", "POST", "/api/orders", '{"item":"x"}', timestamp=1000000)
        assert svc.verify("inst-1", "c1", "POST", "/api/orders", '{"item":"x"}', signed.signature, 1000000)

    def test_bad_signature(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        svc.configure("inst-1", SigningConfig(consumer_id="c1"), secret="b" * 32)
        assert not svc.verify("inst-1", "c1", "POST", "/api", "body", "badsig", 1000)

    def test_sha512(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        svc.configure("inst-1", SigningConfig(consumer_id="c1", algorithm="sha512"), secret="c" * 32)
        signed = svc.sign("inst-1", "c1", "GET", "/api", "", timestamp=1000)
        assert len(signed.signature) == 128  # sha512 hex

    def test_custom_headers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        svc.configure("inst-1", SigningConfig(consumer_id="c1", header_name="X-HMAC", timestamp_header="X-TS"), secret="d" * 32)
        signed = svc.sign("inst-1", "c1", "GET", "/", "", timestamp=1)
        assert "X-HMAC" in signed.headers and "X-TS" in signed.headers

    def test_short_secret_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        with pytest.raises(ValueError, match="at least 32"):
            svc.configure("inst-1", SigningConfig(consumer_id="c1"), secret="short")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestSigning()
        svc.configure("inst-1", SigningConfig(consumer_id="c1"), secret="e" * 32)
        assert not svc.verify("inst-2", "c1", "GET", "/", "", "sig", 1)
