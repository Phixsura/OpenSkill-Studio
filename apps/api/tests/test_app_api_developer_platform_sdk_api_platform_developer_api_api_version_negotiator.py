import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_version_negotiator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator

class TestApiVersionNegotiator:
    def test_explicit_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator()
        svc.register_version("inst-1", "v1")
        svc.register_version("inst-1", "v2")
        vc = svc.negotiate("inst-1", requested="v1")
        assert vc.version == "v1"

    def test_accept_header(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator()
        svc.register_version("inst-1", "v2")
        vc = svc.negotiate("inst-1", accept_header="application/vnd.api.v2+json")
        assert vc.version == "v2"

    def test_default_fallback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator()
        svc.register_version("inst-1", "v1")
        svc.register_version("inst-1", "v2")
        svc.set_default("inst-1", "v1")
        vc = svc.negotiate("inst-1")
        assert vc.version == "v1"

    def test_sunset_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator()
        svc.register_version("inst-1", "v1", status="sunset")
        with pytest.raises(ValueError, match="sunset"):
            svc.negotiate("inst-1", requested="v1")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator()
        svc.register_version("inst-1", "v1")
        assert len(svc.list_versions("inst-2")) == 0
