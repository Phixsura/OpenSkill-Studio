import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_endpoint_dependency_graph import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph

class TestEndpointDependencyGraph:
    def test_add_dependency(self):
        g = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph()
        g.add_endpoint("inst-1", "e1", "GET", "/users")
        g.add_endpoint("inst-1", "e2", "GET", "/orders")
        g.add_dependency("inst-1", "e2", "e1")
        assert g.get_dependencies("inst-1", "e2") == ["e1"]
        assert g.get_dependents("inst-1", "e1") == ["e2"]

    def test_self_dependency_rejected(self):
        g = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph()
        g.add_endpoint("inst-1", "e1", "GET", "/users")
        with pytest.raises(ValueError, match="Self-dependency"):
            g.add_dependency("inst-1", "e1", "e1")

    def test_cycle_detection(self):
        g = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph()
        g.add_endpoint("inst-1", "a", "GET", "/a")
        g.add_endpoint("inst-1", "b", "GET", "/b")
        g.add_endpoint("inst-1", "c", "GET", "/c")
        g.add_dependency("inst-1", "a", "b")
        g.add_dependency("inst-1", "b", "c")
        g.add_dependency("inst-1", "c", "a")
        cycles = g.detect_cycles("inst-1")
        assert len(cycles) > 0

    def test_impact_analysis(self):
        g = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph()
        g.add_endpoint("inst-1", "e1", "GET", "/a")
        g.add_endpoint("inst-1", "e2", "GET", "/b")
        g.add_endpoint("inst-1", "e3", "GET", "/c")
        g.add_dependency("inst-1", "e2", "e1")
        g.add_dependency("inst-1", "e3", "e2")
        affected = g.impact_analysis("inst-1", "e1")
        assert "e2" in affected
        assert "e3" in affected

    def test_isolation(self):
        g = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph()
        g.add_endpoint("inst-1", "e1", "GET", "/a")
        assert g.get_dependencies("inst-2", "e1") == []
