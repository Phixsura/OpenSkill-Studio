import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_endpoint_health_probe import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe

class TestEndpointHealthProbe:
    def test_configure(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe()
        c = p.configure("inst-1", "/health", 30)
        assert c.interval_seconds == 30

    def test_healthy_result(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe()
        p.configure("inst-1", "/health", 30)
        c = p.record_result("inst-1", "/health", 200, 50)
        assert c.last_result.healthy is True
        assert c.consecutive_failures == 0

    def test_unhealthy_result(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe()
        p.configure("inst-1", "/health", 30)
        p.record_result("inst-1", "/health", 500, 50)
        p.record_result("inst-1", "/health", 500, 50)
        assert len(p.unhealthy_probes("inst-1")) == 1

    def test_success_rate(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe()
        p.configure("inst-1", "/health", 30)
        for _ in range(9): p.record_result("inst-1", "/health", 200, 50)
        p.record_result("inst-1", "/health", 500, 50)
        assert p.all_probes("inst-1")[0].success_rate == 90.0

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbe()
        p.configure("inst-1", "/health", 30)
        assert len(p.all_probes("inst-2")) == 0
