import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_api_endpoint_dependency_mapper import AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper

class TestEndpointDependencyMapper:
    def test_add(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper()
        e = m.add_dependency("inst-1", "/api/orders", "/api/users")
        assert "/api/users" in e.depends_on

    def test_self_dependency_rejected(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper()
        with pytest.raises(ValueError):
            m.add_dependency("inst-1", "/api/users", "/api/users")

    def test_depended_by(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper()
        m.add_dependency("inst-1", "/api/orders", "/api/users")
        m.add_dependency("inst-1", "/api/billing", "/api/users")
        impact = m.impact_of("inst-1", "/api/users")
        assert len(impact) == 2

    def test_critical(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper()
        for i in range(5):
            m.add_dependency("inst-1", f"/api/svc{i}", "/api/auth")
        assert len(m.critical_endpoints("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper()
        m.add_dependency("inst-1", "/a", "/b")
        assert len(m.all_endpoints("inst-2")) == 0
