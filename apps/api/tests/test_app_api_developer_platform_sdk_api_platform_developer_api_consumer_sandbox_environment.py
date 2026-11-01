import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_sandbox_environment import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment, SandboxStatus,
)

class TestConsumerSandboxEnvironment:
    def test_create_and_use(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment()
        env = svc.create("inst-1", "c1", "sb-1")
        assert env.status == SandboxStatus.ACTIVE
        env = svc.use_request("inst-1", "sb-1")
        assert env.request_count == 1

    def test_request_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment()
        svc.create("inst-1", "c1", "sb-1", request_limit=100)
        for _ in range(100): svc.use_request("inst-1", "sb-1")
        with pytest.raises(ValueError, match="limit"):
            svc.use_request("inst-1", "sb-1")

    def test_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment()
        svc.create("inst-1", "c1", "sb-1", request_limit=100)
        svc.use_request("inst-1", "sb-1")
        svc.reset("inst-1", "sb-1")
        env = svc._get("inst-1", "sb-1")
        assert env.request_count == 0 and env.reset_count == 1

    def test_paused_blocks_use(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment()
        svc.create("inst-1", "c1", "sb-1")
        svc.pause("inst-1", "sb-1")
        with pytest.raises(ValueError, match="paused"):
            svc.use_request("inst-1", "sb-1")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment()
        svc.create("inst-1", "c1", "sb-1")
        assert len(svc.list_sandboxes("inst-2")) == 0
