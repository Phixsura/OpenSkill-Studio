"""Tests for Endpoint Dependency Health service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_dep_health import (
    DependencyHealthMonitor, Dependency,
)


class TestDependencyHealthMonitor:
    def test_register_and_matrix(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "PostgreSQL", "database"))
        svc.register(Dependency("cache", "Redis", "cache"))
        matrix = svc.get_health_matrix()
        assert len(matrix) == 2

    def test_update_health(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        result = svc.update_health("db", False, latency_ms=500.0, error_rate=0.15)
        assert result["healthy"] is False
        assert result["changed"] is True

    def test_cascade_impact(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        svc.add_dependent("db", "ep1")
        svc.add_dependent("db", "ep2")
        svc.add_dependent("db", "ep3")
        svc.add_dependent("db", "ep4")
        svc.update_health("db", False)
        impact = svc.get_cascade_impact("db")
        assert impact["affected_count"] == 4
        assert impact["severity"] == "high"

    def test_healthy_no_impact(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        svc.add_dependent("db", "ep1")
        impact = svc.get_cascade_impact("db")
        assert impact["severity"] == "none"

    def test_get_unhealthy(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        svc.register(Dependency("cache", "Redis", "cache"))
        svc.update_health("db", False)
        unhealthy = svc.get_unhealthy()
        assert len(unhealthy) == 1
        assert unhealthy[0]["dep_id"] == "db"

    def test_endpoint_deps(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        svc.register(Dependency("cache", "Redis", "cache"))
        svc.add_dependent("db", "ep1")
        svc.add_dependent("cache", "ep1")
        deps = svc.get_endpoint_deps("ep1")
        assert len(deps) == 2

    def test_stats(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        svc.register(Dependency("cache", "Redis", "cache"))
        svc.update_health("cache", False)
        stats = svc.get_stats()
        assert stats["healthy"] == 1
        assert stats["unhealthy"] == 1

    def test_duplicate_rejected(self):
        svc = DependencyHealthMonitor()
        svc.register(Dependency("db", "DB", "database"))
        with pytest.raises(ValueError):
            svc.register(Dependency("db", "DB2", "database"))

    def test_not_found(self):
        svc = DependencyHealthMonitor()
        with pytest.raises(ValueError):
            svc.update_health("missing", False)

    def test_isolation(self):
        a, b = DependencyHealthMonitor(), DependencyHealthMonitor()
        a.register(Dependency("db", "DB", "database"))
        assert b.get_stats()["total"] == 0
