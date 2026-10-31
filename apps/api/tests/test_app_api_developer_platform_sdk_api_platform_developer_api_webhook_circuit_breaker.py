import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_circuit_breaker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker, CircuitState,
)

class TestWebhookCircuitBreaker:
    def test_trips_on_failures(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1", failure_threshold=3)
        for _ in range(3): svc.record_failure("inst-1", "c1")
        cb = svc._breakers[("inst-1", "c1")]
        assert cb.state == CircuitState.OPEN
        assert svc.should_allow("inst-1", "c1") is False

    def test_recovery_to_half_open(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1", failure_threshold=2, recovery_timeout_s=0)
        svc.record_failure("inst-1", "c1")
        svc.record_failure("inst-1", "c1")
        # recovery_timeout=0 means immediate transition
        assert svc.should_allow("inst-1", "c1") is True
        cb = svc._breakers[("inst-1", "c1")]
        assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_success_closes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1", failure_threshold=1, recovery_timeout_s=0, half_open_max=2)
        svc.record_failure("inst-1", "c1")
        svc.should_allow("inst-1", "c1")  # transitions to half_open
        svc.record_success("inst-1", "c1")
        svc.record_success("inst-1", "c1")
        assert svc._breakers[("inst-1", "c1")].state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1", failure_threshold=1, recovery_timeout_s=0)
        svc.record_failure("inst-1", "c1")
        svc.should_allow("inst-1", "c1")  # half_open
        svc.record_failure("inst-1", "c1")
        assert svc._breakers[("inst-1", "c1")].state == CircuitState.OPEN

    def test_reset(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1", failure_threshold=1)
        svc.record_failure("inst-1", "c1")
        svc.reset("inst-1", "c1")
        assert svc._breakers[("inst-1", "c1")].state == CircuitState.CLOSED

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker()
        svc.get_or_create("inst-1", "c1")
        assert svc.should_allow("inst-2", "c1") is True
