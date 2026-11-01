import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_dependency_map import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap, Dependency,
)

class TestEndpointDependencyMap:
    def test_add_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        svc.add_dependency("inst-1", Dependency(from_endpoint="/orders", to_endpoint="/users", dependency_type="calls"))
        deps = svc.get_dependencies("inst-1", "/orders")
        assert len(deps) == 1 and deps[0].to_endpoint == "/users"

    def test_dependents(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        svc.add_dependency("inst-1", Dependency(from_endpoint="/orders", to_endpoint="/users"))
        svc.add_dependency("inst-1", Dependency(from_endpoint="/billing", to_endpoint="/users"))
        dependents = svc.get_dependents("inst-1", "/users")
        assert len(dependents) == 2

    def test_impact_analysis(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        svc.add_dependency("inst-1", Dependency(from_endpoint="/orders", to_endpoint="/db", critical=True))
        svc.add_dependency("inst-1", Dependency(from_endpoint="/checkout", to_endpoint="/orders"))
        impact = svc.analyze_impact("inst-1", "/db")
        assert "/orders" in impact.direct_dependents
        assert "/checkout" in impact.transitive_dependents
        assert impact.critical_chain

    def test_self_dependency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        with pytest.raises(ValueError, match="Self-dependency"):
            svc.add_dependency("inst-1", Dependency(from_endpoint="/x", to_endpoint="/x"))

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        svc.add_dependency("inst-1", Dependency(from_endpoint="/a", to_endpoint="/b"))
        svc.remove_dependency("inst-1", "/a", "/b")
        assert len(svc.list_all("inst-1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap()
        svc.add_dependency("inst-1", Dependency(from_endpoint="/a", to_endpoint="/b"))
        assert len(svc.list_all("inst-2")) == 0
