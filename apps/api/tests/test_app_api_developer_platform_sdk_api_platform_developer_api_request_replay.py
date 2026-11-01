import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_request_replay import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay, CapturedRequest, ReplayStatus,
)

class TestRequestReplay:
    def test_capture_and_replay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay()
        req = CapturedRequest(request_id="r1", method="POST", path="/api/v1/users", body='{"name":"test"}')
        svc.capture("inst-1", req)
        result = svc.replay("inst-1", "r1", 200, 50.0)
        assert result.status == ReplayStatus.SUCCESS
        assert result.duration_ms == 50.0

    def test_header_redaction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay()
        req = CapturedRequest(request_id="r1", method="GET", path="/api", headers={"Authorization": "Bearer secret", "Content-Type": "application/json"})
        captured = svc.capture("inst-1", req)
        assert captured.headers["Authorization"] == "[REDACTED]"
        assert captured.headers["Content-Type"] == "application/json"

    def test_replay_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay()
        with pytest.raises(KeyError):
            svc.replay("inst-1", "nope", 200, 10.0)

    def test_failed_replay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay()
        svc.capture("inst-1", CapturedRequest(request_id="r1", method="GET", path="/x"))
        result = svc.replay("inst-1", "r1", 500, 100.0)
        assert result.status == ReplayStatus.FAILED

    def test_stats_and_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplay()
        svc.capture("inst-1", CapturedRequest(request_id="r1", method="GET", path="/a"))
        svc.replay("inst-1", "r1", 200, 10.0)
        s = svc.stats("inst-1")
        assert s["captured"] == 1 and s["replayed"] == 1 and s["successful"] == 1
        assert svc.stats("inst-2") == {"captured": 0, "replayed": 0, "successful": 0}
