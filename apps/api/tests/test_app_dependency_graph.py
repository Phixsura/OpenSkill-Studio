"""Tests for App Service Dependency Graph — deps, impact, cycles, topo sort."""

import pytest

from app.services.app_dependency_graph import AppDependencyGraph


class TestAddService:
    def test_add(self):
        g = AppDependencyGraph()
        n = g.add_service("inst-1", "api", "API Gateway", depends_on=["auth", "db"])
        assert n.depends_on == ["auth", "db"]

    def test_duplicate(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "api", "API")
        with pytest.raises(ValueError, match="already exists"):
            g.add_service("inst-1", "api", "API2")


class TestDependencies:
    def test_direct_deps(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "api", "API", depends_on=["auth", "db"])
        assert g.get_dependencies("inst-1", "api") == ["auth", "db"]

    def test_dependents(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "db", "Database")
        g.add_service("inst-1", "api", "API", depends_on=["db"])
        g.add_service("inst-1", "worker", "Worker", depends_on=["db"])
        deps = g.get_dependents("inst-1", "db")
        assert set(deps) == {"api", "worker"}


class TestImpact:
    def test_transitive_impact(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "db", "Database")
        g.add_service("inst-1", "api", "API", depends_on=["db"])
        g.add_service("inst-1", "frontend", "Frontend", depends_on=["api"])
        impact = g.get_impact("inst-1", "db")
        assert impact == ["api", "frontend"]

    def test_no_impact(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "standalone", "Standalone")
        assert g.get_impact("inst-1", "standalone") == []


class TestCircular:
    def test_no_cycle(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "a", "A")
        g.add_service("inst-1", "b", "B", depends_on=["a"])
        assert g.has_circular("inst-1") is False

    def test_cycle(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "a", "A", depends_on=["b"])
        g.add_service("inst-1", "b", "B", depends_on=["a"])
        assert g.has_circular("inst-1") is True


class TestTopologicalSort:
    def test_order(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "db", "DB")
        g.add_service("inst-1", "cache", "Cache")
        g.add_service("inst-1", "api", "API", depends_on=["db", "cache"])
        g.add_service("inst-1", "web", "Web", depends_on=["api"])
        order = g.topological_sort("inst-1")
        assert order.index("db") < order.index("api")
        assert order.index("cache") < order.index("api")
        assert order.index("api") < order.index("web")

    def test_circular_raises(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "a", "A", depends_on=["b"])
        g.add_service("inst-1", "b", "B", depends_on=["a"])
        with pytest.raises(ValueError, match="circular"):
            g.topological_sort("inst-1")


class TestIsolation:
    def test_cross_installation(self):
        g = AppDependencyGraph()
        g.add_service("inst-1", "api", "API")
        with pytest.raises(KeyError):
            g.get_dependencies("inst-2", "api")
