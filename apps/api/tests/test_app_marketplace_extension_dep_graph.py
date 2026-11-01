from app.services.app_marketplace_extension_dep_graph import DepGraphService


def test_register_and_direct_deps():
    svc = DepGraphService()
    svc.register("app", "1.0", [("lib-a", "^2.0"), ("lib-b", "^1.0")])
    deps = svc.get_direct_deps("app")
    assert len(deps) == 2


def test_transitive_deps():
    svc = DepGraphService()
    svc.register("app", "1.0", [("lib-a", "^1.0")])
    svc.register("lib-a", "1.0", [("lib-b", "^1.0")])
    svc.register("lib-b", "1.0", [])
    all_deps = svc.get_all_deps("app")
    assert all_deps == {"lib-a", "lib-b"}


def test_cycle_detection():
    svc = DepGraphService()
    svc.register("a", "1.0", [("b", "1.0")])
    svc.register("b", "1.0", [("c", "1.0")])
    svc.register("c", "1.0", [("a", "1.0")])
    cycle = svc.detect_cycles("a")
    assert cycle is not None
    assert "a" in cycle


def test_no_cycle():
    svc = DepGraphService()
    svc.register("a", "1.0", [("b", "1.0")])
    svc.register("b", "1.0", [])
    assert svc.detect_cycles("a") is None


def test_topological_sort():
    svc = DepGraphService()
    svc.register("app", "1.0", [("lib-a", "^1.0"), ("lib-b", "^1.0")])
    svc.register("lib-a", "1.0", [("core", "^1.0")])
    svc.register("lib-b", "1.0", [("core", "^1.0")])
    svc.register("core", "1.0", [])
    order = svc.topological_sort("app")
    assert order is not None
    assert order.index("core") < order.index("lib-a")
    assert order.index("core") < order.index("lib-b")
    assert order[-1] == "app"


def test_version_conflicts():
    svc = DepGraphService()
    svc.register("a", "1.0", [("shared", "^1.0")])
    svc.register("b", "1.0", [("shared", "^2.0")])
    conflicts = svc.find_conflicts(["a", "b"])
    assert len(conflicts) == 1
    assert conflicts[0]["dependency"] == "shared"


def test_get_dependents():
    svc = DepGraphService()
    svc.register("app1", "1.0", [("core", "1.0")])
    svc.register("app2", "1.0", [("core", "1.0")])
    svc.register("core", "1.0", [])
    dependents = svc.get_dependents("core")
    assert set(dependents) == {"app1", "app2"}
