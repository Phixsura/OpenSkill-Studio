from app.services.app_marketplace_extension_dep_resolver import ExtDepResolverService

def test_resolve():
    svc = ExtDepResolverService()
    svc.register("core", "1.0")
    svc.register("auth", "1.0", [("core", "1.0", False)])
    svc.register("app", "1.0", [("auth", "1.0", False), ("core", "1.0", False)])
    resolved, missing = svc.resolve("app")
    assert resolved == ["core", "auth", "app"]
    assert missing == []

def test_missing_dep():
    svc = ExtDepResolverService()
    svc.register("app", "1.0", [("missing", "1.0", False)])
    resolved, missing = svc.resolve("app")
    assert "missing" in missing

def test_circular():
    svc = ExtDepResolverService()
    svc.register("a", "1.0", [("b", "1.0", False)])
    svc.register("b", "1.0", [("a", "1.0", False)])
    cycle = svc.check_circular("a")
    assert cycle is not None
    assert "a" in cycle and "b" in cycle

def test_dependents():
    svc = ExtDepResolverService()
    svc.register("core", "1.0")
    svc.register("auth", "1.0", [("core", "1.0", False)])
    svc.register("ui", "1.0", [("core", "1.0", False)])
    assert set(svc.get_dependents("core")) == {"auth", "ui"}
