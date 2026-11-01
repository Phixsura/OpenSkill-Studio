import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_service_dependency_health import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth, ServiceDependency,
)

class TestConsumerApiServiceDependencyHealth:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_all_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="Database", endpoint="db:5432"))
        svc.register("inst-1", ServiceDependency(service_id="cache", name="Cache", endpoint="redis:6379"))
        svc.update_status("inst-1", "db", "healthy", 5.0, self._now())
        svc.update_status("inst-1", "cache", "healthy", 1.0, self._now())
        report = svc.get_report("inst-1")
        assert report.overall_status == "healthy" and report.healthy_count == 2

    def test_required_down(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="DB", endpoint="db:5432", criticality="required"))
        svc.update_status("inst-1", "db", "down", 0, self._now())
        report = svc.get_report("inst-1")
        assert report.overall_status == "down"

    def test_optional_down_degrades(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="DB", endpoint="db:5432", criticality="required", status="healthy"))
        svc.register("inst-1", ServiceDependency(service_id="search", name="Search", endpoint="es:9200", criticality="optional"))
        svc.update_status("inst-1", "search", "down", 0, self._now())
        report = svc.get_report("inst-1")
        assert report.overall_status == "degraded"

    def test_update_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="DB", endpoint="db:5432"))
        svc.update_status("inst-1", "db", "degraded", 500, self._now())
        deps = svc.list_dependencies("inst-1")
        assert deps[0].status == "degraded" and deps[0].response_time_ms == 500

    def test_invalid_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="DB", endpoint="x"))
        with pytest.raises(ValueError, match="Invalid status"):
            svc.update_status("inst-1", "db", "broken")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth()
        svc.register("inst-1", ServiceDependency(service_id="db", name="DB", endpoint="x"))
        assert len(svc.list_dependencies("inst-2")) == 0
