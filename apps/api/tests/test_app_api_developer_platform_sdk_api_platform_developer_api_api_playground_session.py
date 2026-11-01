import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_playground_session import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession, PlaygroundSession, PlaygroundRequest,
)

class TestApiPlaygroundSession:
    def test_create_and_add(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession()
        svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))
        req = svc.add_request("inst-1", "s1", PlaygroundRequest(request_id="r1", method="GET", path="/users", response_status=200))
        assert req.method == "GET"
        s = svc.get_session("inst-1", "s1")
        assert len(s.requests) == 1

    def test_max_requests(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession(max_requests_per_session=10)
        svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))
        for i in range(10): svc.add_request("inst-1", "s1", PlaygroundRequest(request_id=f"r{i}", method="GET", path="/a"))
        with pytest.raises(ValueError, match="Max requests"):
            svc.add_request("inst-1", "s1", PlaygroundRequest(request_id="r99", method="GET", path="/a"))

    def test_body_truncation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession()
        svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))
        big = "x" * 10000
        req = svc.add_request("inst-1", "s1", PlaygroundRequest(request_id="r1", method="POST", path="/a", body=big))
        assert len(req.body) < 10000

    def test_duplicate_session(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession()
        svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession()
        svc.create_session("inst-1", PlaygroundSession(session_id="s1", developer_id="d1"))
        assert svc.session_count("inst-2") == 0
