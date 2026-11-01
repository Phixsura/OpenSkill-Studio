import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_request_replay import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay, ReplayableRequest,
)

class TestConsumerApiRequestReplay:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_store_and_replay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        svc.store("inst-1", "c1", ReplayableRequest(request_id="r1", method="GET", path="/api/users", original_status=200, original_at=self._now()))
        result = svc.replay("inst-1", "c1", "r1", self._now())
        assert result.replay_status == 200 and not result.diff_detected

    def test_header_redaction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        req = svc.store("inst-1", "c1", ReplayableRequest(request_id="r1", method="GET", path="/api", headers={"Authorization": "Bearer secret", "Content-Type": "application/json"}))
        assert req.headers["Authorization"] == "***"
        assert req.headers["Content-Type"] == "application/json"

    def test_replay_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        with pytest.raises(ValueError, match="not found"):
            svc.replay("inst-1", "c1", "missing", self._now())

    def test_replay_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        svc.store("inst-1", "c1", ReplayableRequest(request_id="r1", method="GET", path="/api"))
        svc.replay("inst-1", "c1", "r1", self._now())
        assert len(svc.get_replays("inst-1", "c1")) == 1

    def test_stored_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        svc.store("inst-1", "c1", ReplayableRequest(request_id="r1", method="GET", path="/a"))
        svc.store("inst-1", "c1", ReplayableRequest(request_id="r2", method="POST", path="/b"))
        assert len(svc.get_stored("inst-1", "c1")) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay()
        svc.store("inst-1", "c1", ReplayableRequest(request_id="r1", method="GET", path="/api"))
        assert len(svc.get_stored("inst-2", "c1")) == 0
