import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_sandbox_environment import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment, SandboxConfig, SandboxRequest,
)

class TestConsumerSandboxEnvironment:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        sb = svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        assert sb.status == "active"
        got = svc.get("inst-1", "sb1")
        assert got.name == "Test"

    def test_record_and_get_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        svc.record_request("inst-1", "sb1", SandboxRequest(request_id="r1", method="GET", path="/api/users", timestamp=self._now(), response_status=200, mocked=True))
        reqs = svc.get_requests("inst-1", "sb1")
        assert len(reqs) == 1 and reqs[0].mocked

    def test_destroy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        svc.destroy("inst-1", "sb1")
        assert svc.get("inst-1", "sb1").status == "destroyed"

    def test_cannot_request_destroyed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        svc.destroy("inst-1", "sb1")
        with pytest.raises(ValueError, match="not active"):
            svc.record_request("inst-1", "sb1", SandboxRequest(request_id="r1", method="GET", path="/x", timestamp=self._now(), response_status=200, mocked=True))

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        with pytest.raises(ValueError, match="already exists"):
            svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test2", created_at=self._now()))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment()
        svc.create("inst-1", SandboxConfig(sandbox_id="sb1", consumer_id="c1", name="Test", created_at=self._now()))
        assert len(svc.list_sandboxes("inst-2")) == 0
