import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_circuit_breaker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker, CircuitBreakerConfig,
)

class TestEndpointCircuitBreaker:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_closed_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api", failure_threshold=3))
        assert svc.is_allowed("inst-1", "/api", self._now())

    def test_trips_open(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api", failure_threshold=3))
        for _ in range(3):
            svc.record_failure("inst-1", "/api", self._now())
        assert svc.get_state("inst-1", "/api").state == "open"
        assert not svc.is_allowed("inst-1", "/api", self._now())

    def test_half_open_after_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api", failure_threshold=2, timeout_seconds=10))
        svc.record_failure("inst-1", "/api", self._now())
        svc.record_failure("inst-1", "/api", self._now())
        assert svc.is_allowed("inst-1", "/api", self._now() + timedelta(seconds=15))
        assert svc.get_state("inst-1", "/api").state == "half_open"

    def test_closes_after_successes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api", failure_threshold=2, success_threshold=2, timeout_seconds=5))
        svc.record_failure("inst-1", "/api", self._now())
        svc.record_failure("inst-1", "/api", self._now())
        svc.is_allowed("inst-1", "/api", self._now() + timedelta(seconds=10))  # triggers half_open
        svc.record_success("inst-1", "/api")
        svc.record_success("inst-1", "/api")
        assert svc.get_state("inst-1", "/api").state == "closed"

    def test_half_open_failure_reopens(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api", failure_threshold=1, timeout_seconds=5))
        svc.record_failure("inst-1", "/api", self._now())
        svc.is_allowed("inst-1", "/api", self._now() + timedelta(seconds=10))
        svc.record_failure("inst-1", "/api", self._now() + timedelta(seconds=10))
        assert svc.get_state("inst-1", "/api").state == "open"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker()
        svc.configure("inst-1", CircuitBreakerConfig(endpoint_path="/api"))
        assert svc.get_state("inst-2", "/api") is None
