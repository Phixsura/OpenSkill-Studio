import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_content_negotiation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation, ContentPreference,
)

class TestContentNegotiation:
    def test_preferred_format(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation()
        svc.set_preference("inst-1", ContentPreference(consumer_id="c1", preferred_format="xml", accepted_formats=["xml", "json"]))
        assert svc.negotiate("inst-1", "c1", ["json", "xml"]) == "xml"

    def test_fallback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation()
        svc.set_preference("inst-1", ContentPreference(consumer_id="c1", preferred_format="protobuf", accepted_formats=["protobuf", "json"]))
        assert svc.negotiate("inst-1", "c1", ["json", "xml"]) == "json"

    def test_default_json(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation()
        assert svc.negotiate("inst-1", "c1", ["json"]) == "json"

    def test_invalid_format(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation()
        with pytest.raises(ValueError, match="Invalid format"):
            svc.set_preference("inst-1", ContentPreference(consumer_id="c1", preferred_format="html"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation()
        svc.set_preference("inst-1", ContentPreference(consumer_id="c1"))
        assert len(svc.list_preferences("inst-2")) == 0
