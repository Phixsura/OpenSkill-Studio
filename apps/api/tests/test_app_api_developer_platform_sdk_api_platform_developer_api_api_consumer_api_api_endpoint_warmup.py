from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_warmup import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup, WarmupTarget,
)

class TestEndpointWarmup:
    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup()
        svc.create_plan("inst-1", "p1", [WarmupTarget("/users", "GET"), WarmupTarget("/orders", "GET")])
        assert svc.progress("inst-1", "p1") == 0.0

    def test_complete_targets(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup()
        svc.create_plan("inst-1", "p1", [WarmupTarget("/users", "GET"), WarmupTarget("/orders", "GET")])
        svc.complete_target("inst-1", "p1", "/users", "GET", 50.0)
        assert svc.progress("inst-1", "p1") == 50.0
        svc.complete_target("inst-1", "p1", "/orders", "GET", 30.0)
        assert svc.is_complete("inst-1", "p1") is True

    def test_empty_targets_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup()
        import pytest
        with pytest.raises(ValueError, match="At least one"):
            svc.create_plan("inst-1", "p1", [])

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup()
        svc.create_plan("inst-1", "p1", [WarmupTarget("/api", "GET")])
        assert len(svc.list_plans("inst-2")) == 0
