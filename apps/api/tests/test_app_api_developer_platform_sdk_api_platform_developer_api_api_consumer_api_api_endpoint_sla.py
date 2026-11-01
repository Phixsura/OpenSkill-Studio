from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_sla import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla, EndpointSla,
)

class TestEndpointSla:
    def test_meeting_sla(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla()
        svc.set_sla("inst-1", EndpointSla(endpoint="/api", method="GET", target_uptime_pct=99.9, target_latency_p99_ms=500))
        svc.update_actuals("inst-1", "/api", "GET", uptime=99.95, latency_p99=200, error_rate=0.5)
        sla = svc._slas[("inst-1", "GET", "/api")]
        assert sla.meeting_sla is True

    def test_sla_violation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla()
        svc.set_sla("inst-1", EndpointSla(endpoint="/api", method="GET"))
        svc.update_actuals("inst-1", "/api", "GET", uptime=98.0, latency_p99=1000, error_rate=5.0)
        assert len(svc.violations("inst-1")) == 1
        sla = svc._slas[("inst-1", "GET", "/api")]
        assert len(sla.violations) == 3

    def test_invalid_uptime_target(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla()
        import pytest
        with pytest.raises(ValueError):
            svc.set_sla("inst-1", EndpointSla(endpoint="/api", method="GET", target_uptime_pct=50))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointSla()
        svc.set_sla("inst-1", EndpointSla(endpoint="/api", method="GET"))
        assert len(svc.list_slas("inst-2")) == 0
