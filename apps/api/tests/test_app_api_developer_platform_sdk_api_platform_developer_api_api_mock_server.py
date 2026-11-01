import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_mock_server import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer, MockResponse,
)

class TestApiMockServer:
    def test_register_and_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        svc.register_mock("inst-1", MockResponse(mock_id="m1", method="GET", path="/users", status_code=200, body='[{"id":"u1"}]'))
        m = svc.match("inst-1", "GET", "/users")
        assert m is not None and m.status_code == 200 and m.hit_count == 1

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        assert svc.match("inst-1", "GET", "/nope") is None

    def test_invalid_json_body(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        with pytest.raises(ValueError, match="Invalid JSON"):
            svc.register_mock("inst-1", MockResponse(mock_id="m1", method="GET", path="/a", body="not json"))

    def test_hit_counting(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        svc.register_mock("inst-1", MockResponse(mock_id="m1", method="POST", path="/api", body='{}'))
        for _ in range(5): svc.match("inst-1", "POST", "/api")
        assert svc.total_hits("inst-1") == 5
        svc.reset_hits("inst-1")
        assert svc.total_hits("inst-1") == 0

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        svc.register_mock("inst-1", MockResponse(mock_id="m1", method="GET", path="/a", body='{}'))
        assert svc.remove_mock("inst-1", "GET", "/a") is True
        assert svc.match("inst-1", "GET", "/a") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer()
        svc.register_mock("inst-1", MockResponse(mock_id="m1", method="GET", path="/a", body='{}'))
        assert svc.match("inst-2", "GET", "/a") is None
