from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_inspector import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector, InspectedRequest,
)

class TestRequestInspector:
    def test_inspect_and_recent(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector()
        svc.inspect("inst-1", InspectedRequest(request_id="r1", method="GET", path="/users", status_code=200, duration_ms=50))
        recent = svc.recent("inst-1")
        assert len(recent) == 1

    def test_header_redaction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector()
        req = svc.inspect("inst-1", InspectedRequest(request_id="r1", method="GET", path="/a", status_code=200, duration_ms=10, request_headers={"Authorization": "Bearer secret", "Content-Type": "json"}))
        assert req.request_headers["Authorization"] == "[REDACTED]"
        assert req.request_headers["Content-Type"] == "json"

    def test_body_truncation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector()
        req = svc.inspect("inst-1", InspectedRequest(request_id="r1", method="POST", path="/a", status_code=200, duration_ms=10, body_preview="x" * 5000))
        assert len(req.body_preview) < 5000

    def test_filter_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector()
        svc.inspect("inst-1", InspectedRequest(request_id="r1", method="GET", path="/a", status_code=200, duration_ms=10))
        svc.inspect("inst-1", InspectedRequest(request_id="r2", method="GET", path="/b", status_code=500, duration_ms=100))
        errors = svc.recent("inst-1", status_min=500)
        assert len(errors) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestInspector()
        svc.inspect("inst-1", InspectedRequest(request_id="r1", method="GET", path="/a", status_code=200, duration_ms=10))
        assert svc.count("inst-2") == 0
