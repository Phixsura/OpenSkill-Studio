from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_context import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext

class TestRequestContext:
    def test_create_context(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext()
        ctx = svc.create_context("inst-1", "c1", region="us-east", api_version="v2")
        assert ctx.request_id.startswith("req-")
        assert ctx.trace_id.startswith("trace-")
        assert ctx.region == "us-east"

    def test_add_metadata(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext()
        ctx = svc.create_context("inst-1", "c1")
        svc.add_metadata("inst-1", ctx.request_id, "user_id", "u123")
        assert ctx.metadata["user_id"] == "u123"

    def test_contexts_by_region(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext()
        svc.create_context("inst-1", "c1", region="us-east")
        svc.create_context("inst-1", "c2", region="eu-west")
        svc.create_context("inst-1", "c3", region="us-east")
        regions = svc.contexts_by_region("inst-1")
        assert regions["us-east"] == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestContext()
        svc.create_context("inst-1", "c1")
        assert svc.active_contexts("inst-2") == 0
