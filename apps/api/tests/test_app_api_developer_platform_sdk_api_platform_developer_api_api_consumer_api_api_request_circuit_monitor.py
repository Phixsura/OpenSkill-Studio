from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_circuit_monitor import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor, CircuitSnapshot,
)

class TestRequestCircuitMonitor:
    def test_update_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor()
        svc.update("inst-1", CircuitSnapshot(endpoint="/users", state="closed"))
        svc.update("inst-1", CircuitSnapshot(endpoint="/orders", state="open", failure_count=10))
        s = svc.summary("inst-1")
        assert s.total_circuits == 2
        assert s.open_count == 1 and s.closed_count == 1
        assert s.most_failures_endpoint == "/orders"

    def test_open_circuits(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor()
        svc.update("inst-1", CircuitSnapshot(endpoint="/a", state="closed"))
        svc.update("inst-1", CircuitSnapshot(endpoint="/b", state="open"))
        assert len(svc.open_circuits("inst-1")) == 1

    def test_empty_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor()
        s = svc.summary("inst-1")
        assert s.total_circuits == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitor()
        svc.update("inst-1", CircuitSnapshot(endpoint="/a", state="closed"))
        assert len(svc.list_circuits("inst-2")) == 0
