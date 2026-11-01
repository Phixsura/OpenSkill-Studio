import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_quota_enforcement import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement, EndpointQuota,
)

class TestEndpointQuotaEnforcement:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_within_quota(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        svc.set_quota("inst-1", EndpointQuota(endpoint_path="/api", consumer_id="c1", max_requests=10, window_seconds=60))
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert result.allowed and result.remaining == 9

    def test_quota_exceeded(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        svc.set_quota("inst-1", EndpointQuota(endpoint_path="/api", consumer_id="c1", max_requests=3, window_seconds=60))
        for _ in range(3):
            svc.check_and_consume("inst-1", "c1", "/api", self._now())
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert not result.allowed and result.retry_after_seconds > 0

    def test_window_reset(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        svc.set_quota("inst-1", EndpointQuota(endpoint_path="/api", consumer_id="c1", max_requests=2, window_seconds=60))
        svc.check_and_consume("inst-1", "c1", "/api", self._now())
        svc.check_and_consume("inst-1", "c1", "/api", self._now())
        result = svc.check_and_consume("inst-1", "c1", "/api", self._now() + timedelta(seconds=120))
        assert result.allowed and result.current == 1

    def test_no_quota_allows(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        result = svc.check_and_consume("inst-1", "c1", "/api/anything", self._now())
        assert result.allowed

    def test_invalid_config(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        with pytest.raises(ValueError, match="max_requests"):
            svc.set_quota("inst-1", EndpointQuota(endpoint_path="/api", consumer_id="c1", max_requests=0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement()
        svc.set_quota("inst-1", EndpointQuota(endpoint_path="/api", consumer_id="c1", max_requests=1))
        svc.check_and_consume("inst-1", "c1", "/api", self._now())
        assert svc.check_and_consume("inst-2", "c1", "/api", self._now()).allowed
