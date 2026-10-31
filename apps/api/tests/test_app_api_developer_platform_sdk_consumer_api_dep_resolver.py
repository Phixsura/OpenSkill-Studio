"""Tests for Dependency Resolver service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_dep_resolver import DependencyResolver


class TestDependencyResolver:
    def test_add_and_resolve(self):
        svc = DependencyResolver()
        svc.add_endpoint("a")
        svc.add_endpoint("b")
        svc.add_endpoint("c")
        svc.add_dependency("c", "b")
        svc.add_dependency("b", "a")
        result = svc.resolve_order()
        assert result["success"] is True
        order = result["order"]
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_cycle_detection(self):
        svc = DependencyResolver()
        svc.add_dependency("a", "b")
        svc.add_dependency("b", "c")
        svc.add_dependency("c", "a")
        result = svc.resolve_order()
        assert result["success"] is False
        assert result["reason"] == "cycles_detected"

    def test_transitive_deps(self):
        svc = DependencyResolver()
        svc.add_dependency("c", "b")
        svc.add_dependency("b", "a")
        deps = svc.get_dependencies("c")
        assert "a" in deps["transitive"]
        assert "b" in deps["transitive"]

    def test_self_dependency_rejected(self):
        svc = DependencyResolver()
        with pytest.raises(ValueError):
            svc.add_dependency("a", "a")

    def test_roots_and_leaves(self):
        svc = DependencyResolver()
        svc.add_dependency("b", "a")
        svc.add_dependency("c", "b")
        assert "a" in svc.get_roots()
        assert "c" in svc.get_leaves()

    def test_remove_dependency(self):
        svc = DependencyResolver()
        svc.add_dependency("b", "a")
        svc.remove_dependency("b", "a")
        deps = svc.get_dependencies("b")
        assert deps["direct"] == []

    def test_independent_endpoints(self):
        svc = DependencyResolver()
        svc.add_endpoint("x")
        svc.add_endpoint("y")
        result = svc.resolve_order()
        assert result["success"] is True
        assert result["total"] == 2

    def test_isolation(self):
        a, b = DependencyResolver(), DependencyResolver()
        a.add_endpoint("ep1")
        assert b.get_roots() == []
