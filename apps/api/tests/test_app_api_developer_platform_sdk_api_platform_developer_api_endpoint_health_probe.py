import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_endpoint_health_probe import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe, HealthProbe, ProbeStatus,
)

class TestEndpointHealthProbe:
    def test_healthy_after_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe()
        svc.create_probe("inst-1", HealthProbe(probe_id="p1", endpoint="/health", healthy_threshold=2))
        svc.record_check("inst-1", "p1", 200, 50.0)
        svc.record_check("inst-1", "p1", 200, 30.0)
        assert svc.get_status("inst-1", "p1") == ProbeStatus.HEALTHY

    def test_unhealthy_after_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe()
        svc.create_probe("inst-1", HealthProbe(probe_id="p1", endpoint="/health", unhealthy_threshold=3))
        for _ in range(3): svc.record_check("inst-1", "p1", 500, 100.0)
        assert svc.get_status("inst-1", "p1") == ProbeStatus.UNHEALTHY

    def test_degraded_state(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe()
        svc.create_probe("inst-1", HealthProbe(probe_id="p1", endpoint="/health", unhealthy_threshold=5))
        svc.record_check("inst-1", "p1", 500, 100.0)
        assert svc.get_status("inst-1", "p1") == ProbeStatus.DEGRADED

    def test_recovery(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe()
        svc.create_probe("inst-1", HealthProbe(probe_id="p1", endpoint="/health", healthy_threshold=2, unhealthy_threshold=2))
        svc.record_check("inst-1", "p1", 500, 100.0)
        svc.record_check("inst-1", "p1", 500, 100.0)
        assert svc.get_status("inst-1", "p1") == ProbeStatus.UNHEALTHY
        svc.record_check("inst-1", "p1", 200, 50.0)
        svc.record_check("inst-1", "p1", 200, 50.0)
        assert svc.get_status("inst-1", "p1") == ProbeStatus.HEALTHY

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointHealthProbe()
        svc.create_probe("inst-1", HealthProbe(probe_id="p1", endpoint="/health"))
        assert len(svc.list_probes("inst-2")) == 0
