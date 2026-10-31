import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_playground import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground, PlaygroundRequest, SavedRequest,
)

class TestConsumerApiPlayground:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_execute(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        resp = svc.execute("inst-1", PlaygroundRequest(request_id="r1", consumer_id="c1", method="GET", path="/api/users", created_at=self._now()))
        assert resp.status_code == 200 and "playground" in resp.body

    def test_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        svc.execute("inst-1", PlaygroundRequest(request_id="r1", consumer_id="c1", method="GET", path="/api/users"))
        svc.execute("inst-1", PlaygroundRequest(request_id="r2", consumer_id="c1", method="POST", path="/api/orders"))
        history = svc.get_history("inst-1", "c1")
        assert len(history) == 2

    def test_save_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        req = PlaygroundRequest(request_id="r1", consumer_id="c1", method="GET", path="/api/users")
        svc.save_request("inst-1", "c1", SavedRequest(name="List Users", request=req, description="Get all users"))
        saved = svc.list_saved("inst-1", "c1")
        assert len(saved) == 1 and saved[0].name == "List Users"

    def test_invalid_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        with pytest.raises(ValueError, match="Invalid method"):
            svc.execute("inst-1", PlaygroundRequest(request_id="r1", consumer_id="c1", method="HACK", path="/api"))

    def test_invalid_path(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        with pytest.raises(ValueError, match="Path must start"):
            svc.execute("inst-1", PlaygroundRequest(request_id="r1", consumer_id="c1", method="GET", path="api/users"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground()
        svc.execute("inst-1", PlaygroundRequest(request_id="r1", consumer_id="c1", method="GET", path="/api"))
        assert len(svc.get_history("inst-2", "c1")) == 0
