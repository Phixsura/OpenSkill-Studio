import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_abort_controller import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController, AbortableRequest,
)

class TestRequestAbortController:
    def test_register_and_abort(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController()
        svc.register("inst-1", AbortableRequest(request_id="r1", consumer_id="c1", endpoint="/api"))
        req = svc.abort("inst-1", "r1", "timeout")
        assert req.aborted is True and req.abort_reason == "timeout"

    def test_cannot_abort_completed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController()
        svc.register("inst-1", AbortableRequest(request_id="r1", consumer_id="c1", endpoint="/api"))
        svc.complete("inst-1", "r1")
        with pytest.raises(ValueError, match="completed"):
            svc.abort("inst-1", "r1")

    def test_cannot_complete_aborted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController()
        svc.register("inst-1", AbortableRequest(request_id="r1", consumer_id="c1", endpoint="/api"))
        svc.abort("inst-1", "r1")
        with pytest.raises(ValueError, match="aborted"):
            svc.complete("inst-1", "r1")

    def test_abort_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController()
        svc.register("inst-1", AbortableRequest(request_id="r1", consumer_id="c1", endpoint="/a"))
        svc.register("inst-1", AbortableRequest(request_id="r2", consumer_id="c1", endpoint="/a"))
        svc.complete("inst-1", "r1")
        svc.abort("inst-1", "r2")
        assert svc.abort_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortController()
        svc.register("inst-1", AbortableRequest(request_id="r1", consumer_id="c1", endpoint="/a"))
        assert len(svc.in_flight("inst-2")) == 0
