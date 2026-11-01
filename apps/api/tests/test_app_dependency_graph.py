"""Tests for App Dependency Graph — circular detection, depth, affected services."""

import pytest

from app.services.app_dependency_graph import AppDependencyGraph


class TestRegister:
    def test_register(self):
        g = AppDependencyGraph()
        n = g.register_service("inst-1", "api", "API Service", "v1.0", ["db", "cache"])
        assert n.name == "API Service"
        assert n.depends_on == ["db", "cache"]

    def test_self_dependency(self):
        g = AppDependencyGraph()
        with pytest.raises(ValueError, match="itself"):
            g.register_service("inst-1", "api", "API", depends_on=["api"])


class TestCircular:
    def test_no_circular(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "db", "Database")
        g.register_service("inst-1", "api", "API", depends_on=["db"])
        g.register_service("inst-1", "web", "Web", depends_on=["api"])
        assert g.has_circular("inst-1") is False

    def test_circular(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "a", "A", depends_on=["b"])
        g.register_service("inst-1", "b", "B", depends_on=["c"])
        g.register_service("inst-1", "c", "C", depends_on=["a"])
        assert g.has_circular("inst-1") is True


class TestDepth:
    def test_depth(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "db", "DB")
        g.register_service("inst-1", "cache", "Cache")
        g.register_service("inst-1", "api", "API", depends_on=["db", "cache"])
        g.register_service("inst-1", "web", "Web", depends_on=["api"])
        assert g.dependency_depth("inst-1", "web") == 2

    def test_leaf_depth(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "db", "DB")
        assert g.dependency_depth("inst-1", "db") == 0


class TestAffected:
    def test_affected(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "db", "DB")
        g.register_service("inst-1", "api", "API", depends_on=["db"])
        g.register_service("inst-1", "web", "Web", depends_on=["api"])
        g.register_service("inst-1", "worker", "Worker", depends_on=["db"])
        affected = g.affected_by("inst-1", "db")
        assert "api" in affected
        assert "web" in affected
        assert "worker" in affected


class TestIsolation:
    def test_cross(self):
        g = AppDependencyGraph()
        g.register_service("inst-1", "db", "DB")
        assert g.list_services("inst-2") == []
