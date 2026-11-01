import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_content_negotiation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation, NegotiationConfig,
)

class TestConsumerApiContentNegotiation:
    def test_json_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1", supported_formats=["application/json", "text/csv"]))
        result = svc.negotiate("inst-1", "c1", "application/json")
        assert result.content_type == "application/json" and result.negotiated

    def test_csv_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1", supported_formats=["application/json", "text/csv"]))
        result = svc.negotiate("inst-1", "c1", "text/csv, application/json")
        assert result.content_type == "text/csv"

    def test_fallback_default(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1", supported_formats=["application/json"]))
        result = svc.negotiate("inst-1", "c1", "text/html")
        assert result.content_type == "application/json" and not result.negotiated

    def test_strict_rejects(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1", supported_formats=["application/json"], strict=True))
        with pytest.raises(ValueError, match="No acceptable format"):
            svc.negotiate("inst-1", "c1", "text/html")

    def test_wildcard_accept(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1"))
        result = svc.negotiate("inst-1", "c1", "*/*")
        assert result.content_type == "application/json"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation()
        svc.set_config("inst-1", NegotiationConfig(consumer_id="c1", supported_formats=["text/csv"], default_format="text/csv"))
        assert svc.get_config("inst-2", "c1") is None
