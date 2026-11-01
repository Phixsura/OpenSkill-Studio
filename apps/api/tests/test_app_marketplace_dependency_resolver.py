import pytest
from app.services.app_marketplace_dependency_resolver import (
    DependencyResolver, CyclicDependencyError, MissingDependencyError,
)


def test_simple_chain():
    dr = DependencyResolver()
    dr.register("core")
    dr.register("utils", ["core"])
    dr.register("app", ["utils"])
    order = dr.resolve("app")
    assert order == ["core", "utils", "app"]


def test_diamond_dependency():
    dr = DependencyResolver()
    dr.register("base")
    dr.register("left", ["base"])
    dr.register("right", ["base"])
    dr.register("top", ["left", "right"])
    order = dr.resolve("top")
    assert order.index("base") < order.index("left")
    assert order.index("base") < order.index("right")
    assert order[-1] == "top"


def test_cycle_detection():
    dr = DependencyResolver()
    dr.register("a", ["b"])
    dr.register("b", ["c"])
    dr.register("c", ["a"])
    with pytest.raises(CyclicDependencyError) as exc:
        dr.resolve("a")
    assert len(exc.value.cycle) >= 3


def test_missing_dependency():
    dr = DependencyResolver()
    dr.register("app", ["nonexistent"])
    with pytest.raises(MissingDependencyError):
        dr.resolve("app")


def test_no_dependencies():
    dr = DependencyResolver()
    dr.register("standalone")
    assert dr.resolve("standalone") == ["standalone"]


def test_resolve_all():
    dr = DependencyResolver()
    dr.register("shared")
    dr.register("ext-a", ["shared"])
    dr.register("ext-b", ["shared"])
    order = dr.resolve_all(["ext-a", "ext-b"])
    assert order[0] == "shared"  # shared first
    assert "ext-a" in order
    assert "ext-b" in order


def test_get_dependents():
    dr = DependencyResolver()
    dr.register("lib")
    dr.register("app1", ["lib"])
    dr.register("app2", ["lib"])
    dr.register("app3")
    dependents = dr.get_dependents("lib")
    assert sorted(dependents) == ["app1", "app2"]
