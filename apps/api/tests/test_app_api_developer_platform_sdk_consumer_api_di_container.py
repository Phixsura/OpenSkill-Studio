"""Tests for Consumer API Dependency Injection service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_di_container import DiContainer


class _MockService:
    pass

class _MockWithDep:
    def __init__(self, db=None):
        self.db = db


class TestDiContainer:
    def test_register_instance(self):
        svc = DiContainer()
        instance = _MockService()
        svc.register("db", instance=instance)
        assert svc.resolve("db") is instance

    def test_register_factory(self):
        svc = DiContainer()
        svc.register("svc", factory=_MockService)
        result = svc.resolve("svc")
        assert isinstance(result, _MockService)

    def test_singleton_same_instance(self):
        svc = DiContainer()
        svc.register("svc", factory=_MockService, lifecycle="singleton")
        a = svc.resolve("svc")
        b = svc.resolve("svc")
        assert a is b

    def test_transient_different_instances(self):
        svc = DiContainer()
        svc.register("svc", factory=_MockService, lifecycle="transient")
        a = svc.resolve("svc")
        b = svc.resolve("svc")
        assert a is not b

    def test_dependency_injection(self):
        svc = DiContainer()
        svc.register("db", factory=_MockService)
        svc.register("repo", factory=_MockWithDep, dependencies=["db"])
        repo = svc.resolve("repo")
        assert isinstance(repo.db, _MockService)

    def test_circular_dependency(self):
        svc = DiContainer()
        svc.register("a", factory=_MockService, dependencies=["b"])
        svc.register("b", factory=_MockService, dependencies=["a"])
        with pytest.raises(ValueError, match="Circular"):
            svc.resolve("a")

    def test_not_registered(self):
        svc = DiContainer()
        with pytest.raises(ValueError):
            svc.resolve("missing")

    def test_has(self):
        svc = DiContainer()
        svc.register("db", instance=_MockService())
        assert svc.has("db") is True
        assert svc.has("missing") is False

    def test_list_services(self):
        svc = DiContainer()
        svc.register("a", factory=_MockService)
        svc.register("b", factory=_MockService, lifecycle="transient")
        services = svc.list_services()
        assert len(services) == 2

    def test_dependency_tree(self):
        svc = DiContainer()
        svc.register("db", factory=_MockService)
        svc.register("repo", factory=_MockWithDep, dependencies=["db"])
        tree = svc.get_dependency_tree("repo")
        assert tree["name"] == "repo"
        assert len(tree["dependencies"]) == 1

    def test_reset(self):
        svc = DiContainer()
        svc.register("svc", factory=_MockService)
        svc.resolve("svc")
        result = svc.reset()
        assert result["cleared_instances"] == 1

    def test_duplicate_rejected(self):
        svc = DiContainer()
        svc.register("a", factory=_MockService)
        with pytest.raises(ValueError):
            svc.register("a", factory=_MockService)

    def test_stats(self):
        svc = DiContainer()
        svc.register("a", factory=_MockService, lifecycle="singleton")
        svc.register("b", factory=_MockService, lifecycle="transient")
        svc.resolve("a")
        stats = svc.get_stats()
        assert stats["total_services"] == 2
        assert stats["instantiated"] == 1

    def test_isolation(self):
        a, b = DiContainer(), DiContainer()
        a.register("svc", factory=_MockService)
        assert not b.has("svc")
