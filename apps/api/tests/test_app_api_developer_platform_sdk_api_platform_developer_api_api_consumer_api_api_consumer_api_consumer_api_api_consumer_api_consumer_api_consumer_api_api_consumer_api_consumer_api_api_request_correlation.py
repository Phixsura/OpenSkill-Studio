import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_request_correlation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation, CorrelatedRequest,
)

class TestRequestCorrelation:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_chain(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(correlation_id="root-1", consumer_id="c1", method="GET", path="/api/orders", status_code=200, latency_ms=50, service="gateway", timestamp=self._now()))
        svc.record("inst-1", CorrelatedRequest(correlation_id="child-1", consumer_id="c1", method="GET", path="/api/users/1", status_code=200, latency_ms=30, parent_id="root-1", service="user-svc", timestamp=self._now()))
        chain = svc.get_chain("inst-1", "root-1")
        assert len(chain.requests) == 2 and chain.service_count == 2

    def test_generate_id(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        id1 = svc.generate_id()
        id2 = svc.generate_id()
        assert len(id1) == 32 and id1 != id2

    def test_find_by_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(correlation_id="r1", consumer_id="c1", method="GET", path="/a", timestamp=self._now()))
        svc.record("inst-1", CorrelatedRequest(correlation_id="r2", consumer_id="c2", method="GET", path="/b", timestamp=self._now()))
        roots = svc.find_by_consumer("inst-1", "c1")
        assert len(roots) == 1

    def test_total_latency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(correlation_id="root", consumer_id="c1", method="GET", path="/", latency_ms=100, timestamp=self._now()))
        svc.record("inst-1", CorrelatedRequest(correlation_id="child", consumer_id="c1", method="GET", path="/sub", latency_ms=50, parent_id="root", timestamp=self._now()))
        chain = svc.get_chain("inst-1", "root")
        assert chain.total_latency_ms == 150.0

    def test_empty_chain(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        chain = svc.get_chain("inst-1", "missing")
        assert len(chain.requests) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(correlation_id="r1", consumer_id="c1", method="GET", path="/", timestamp=self._now()))
        assert len(svc.find_by_consumer("inst-2", "c1")) == 0
