from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_circuit_state_manager import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager, CircuitState,
)

class TestCircuitStateManager:
    def test_opens_after_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager(failure_threshold=3)
        for _ in range(3): svc.record_failure("inst-1", "c1", "/api")
        c = svc.get_or_create("inst-1", "c1", "/api")
        assert c.state == CircuitState.OPEN

    def test_blocks_when_open(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager(failure_threshold=2, recovery_s=9999)
        svc.record_failure("inst-1", "c1", "/api")
        svc.record_failure("inst-1", "c1", "/api")
        assert svc.is_allowed("inst-1", "c1", "/api") is False

    def test_recovery_to_half_open(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager(failure_threshold=1, recovery_s=0)
        svc.record_failure("inst-1", "c1", "/api")
        assert svc.is_allowed("inst-1", "c1", "/api") is True  # immediate recovery
        c = svc.get_or_create("inst-1", "c1", "/api")
        assert c.state == CircuitState.HALF_OPEN

    def test_success_closes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager(failure_threshold=1, recovery_s=0)
        svc.record_failure("inst-1", "c1", "/api")
        svc.is_allowed("inst-1", "c1", "/api")  # triggers half_open
        svc.record_success("inst-1", "c1", "/api")
        assert svc.get_or_create("inst-1", "c1", "/api").state == CircuitState.CLOSED

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager()
        svc.get_or_create("inst-1", "c1", "/api")
        assert len(svc.open_circuits("inst-2")) == 0
