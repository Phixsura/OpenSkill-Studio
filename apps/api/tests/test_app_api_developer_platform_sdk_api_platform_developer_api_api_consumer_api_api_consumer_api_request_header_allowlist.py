from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_header_allowlist import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist, HeaderAllowlist,
)

class TestRequestHeaderAllowlist:
    def test_filter_unknown(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist()
        svc.set_allowlist("inst-1", HeaderAllowlist(consumer_id="c1", allowed_headers={"x-custom"}))
        result = svc.filter_headers("inst-1", "c1", {"Content-Type": "json", "X-Custom": "val", "X-Evil": "bad"})
        assert "Content-Type" in result  # default allowed
        assert "X-Custom" in result
        assert "X-Evil" not in result

    def test_no_allowlist_passes_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist()
        result = svc.filter_headers("inst-1", "c1", {"X-Anything": "val"})
        assert "X-Anything" in result

    def test_is_allowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist()
        svc.set_allowlist("inst-1", HeaderAllowlist(consumer_id="c1", allowed_headers={"x-api-version"}))
        assert svc.is_allowed("inst-1", "c1", "X-Api-Version") is True
        assert svc.is_allowed("inst-1", "c1", "X-Forbidden") is False

    def test_default_headers_always_allowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist()
        svc.set_allowlist("inst-1", HeaderAllowlist(consumer_id="c1", allowed_headers=set()))
        assert svc.is_allowed("inst-1", "c1", "Authorization") is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist()
        svc.set_allowlist("inst-1", HeaderAllowlist(consumer_id="c1"))
        assert len(svc.list_allowlists("inst-2")) == 0
