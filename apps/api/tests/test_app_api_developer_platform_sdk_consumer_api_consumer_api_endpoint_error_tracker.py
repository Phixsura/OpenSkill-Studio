import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_endpoint_error_tracker import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker, EndpointError,
)

class TestEndpointErrorTracker:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        svc.record_request("inst-1", "/api/users")
        svc.record_request("inst-1", "/api/users")
        svc.record_error("inst-1", EndpointError(error_id="e1", endpoint_path="/api/users", method="GET", status_code=500, error_code="INTERNAL", message="DB timeout", timestamp=self._now()))
        summary = svc.get_summary("inst-1", "/api/users")
        assert summary.total_errors == 1 and summary.error_rate_pct == 50.0

    def test_most_common_error(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        for _ in range(5):
            svc.record_error("inst-1", EndpointError(error_id="e", endpoint_path="/api", method="GET", status_code=429, error_code="RATE_LIMITED", message="x", timestamp=self._now()))
        svc.record_error("inst-1", EndpointError(error_id="e2", endpoint_path="/api", method="GET", status_code=500, error_code="INTERNAL", message="y", timestamp=self._now()))
        summary = svc.get_summary("inst-1", "/api")
        assert summary.most_common_error == "RATE_LIMITED"

    def test_by_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        svc.record_error("inst-1", EndpointError(error_id="e1", endpoint_path="/api", method="GET", status_code=400, error_code="BAD_REQ", message="x", timestamp=self._now()))
        svc.record_error("inst-1", EndpointError(error_id="e2", endpoint_path="/api", method="POST", status_code=400, error_code="BAD_REQ", message="y", timestamp=self._now()))
        svc.record_error("inst-1", EndpointError(error_id="e3", endpoint_path="/api", method="GET", status_code=500, error_code="INT", message="z", timestamp=self._now()))
        summary = svc.get_summary("inst-1", "/api")
        assert summary.by_status[400] == 2 and summary.by_status[500] == 1

    def test_recent(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        svc.record_error("inst-1", EndpointError(error_id="e1", endpoint_path="/api", method="GET", status_code=500, error_code="INT", message="x", timestamp=self._now()))
        recent = svc.get_recent("inst-1", "/api")
        assert len(recent) == 1

    def test_list_erroring(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        svc.record_error("inst-1", EndpointError(error_id="e1", endpoint_path="/api/a", method="GET", status_code=500, error_code="X", message="x", timestamp=self._now()))
        svc.record_error("inst-1", EndpointError(error_id="e2", endpoint_path="/api/b", method="GET", status_code=500, error_code="Y", message="y", timestamp=self._now()))
        endpoints = svc.list_erroring_endpoints("inst-1")
        assert endpoints == ["/api/a", "/api/b"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointErrorTracker()
        svc.record_error("inst-1", EndpointError(error_id="e1", endpoint_path="/api", method="GET", status_code=500, error_code="X", message="x", timestamp=self._now()))
        assert svc.get_summary("inst-2", "/api").total_errors == 0
