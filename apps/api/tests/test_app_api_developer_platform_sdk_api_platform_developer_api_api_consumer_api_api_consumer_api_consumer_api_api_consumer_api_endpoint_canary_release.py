import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_endpoint_canary_release import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease, CanaryRelease, CanaryMetrics,
)

class TestEndpointCanaryRelease:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        svc.create("inst-1", CanaryRelease(release_id="r1", endpoint_path="/api/users", canary_version="v2", stable_version="v1", canary_weight_pct=10, created_at=self._now()))
        active = svc.list_active("inst-1")
        assert len(active) == 1 and active[0].canary_weight_pct == 10

    def test_analyze_safe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        analysis = svc.analyze(CanaryMetrics(canary_error_rate=0.2, stable_error_rate=0.1, canary_latency_ms=100, stable_latency_ms=95, canary_requests=1000, stable_requests=9000))
        assert analysis.safe_to_promote

    def test_analyze_rollback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        analysis = svc.analyze(CanaryMetrics(canary_error_rate=5.0, stable_error_rate=0.1, canary_latency_ms=500, stable_latency_ms=100, canary_requests=100, stable_requests=900))
        assert not analysis.safe_to_promote and "ROLL BACK" in analysis.recommendation

    def test_promote(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        svc.create("inst-1", CanaryRelease(release_id="r1", endpoint_path="/api", canary_version="v2", stable_version="v1", created_at=self._now()))
        svc.promote("inst-1", "r1")
        assert len(svc.list_active("inst-1")) == 0  # no longer active

    def test_rollback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        svc.create("inst-1", CanaryRelease(release_id="r1", endpoint_path="/api", canary_version="v2", stable_version="v1", created_at=self._now()))
        r = svc.rollback("inst-1", "r1")
        assert r.status == "rolled_back" and r.canary_weight_pct == 0

    def test_update_weight(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        svc.create("inst-1", CanaryRelease(release_id="r1", endpoint_path="/api", canary_version="v2", stable_version="v1", canary_weight_pct=5, created_at=self._now()))
        svc.update_weight("inst-1", "r1", 25)
        assert svc.list_active("inst-1")[0].canary_weight_pct == 25

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointCanaryRelease()
        svc.create("inst-1", CanaryRelease(release_id="r1", endpoint_path="/api", canary_version="v2", stable_version="v1", created_at=self._now()))
        assert len(svc.list_active("inst-2")) == 0
