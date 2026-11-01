from app.services.app_marketplace_extension_sandbox_dependency_injection import (
    SandboxDependencyInjectionService, Lifetime,
)


def test_register_and_resolve():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "logger", "ConsoleLogger")
    result = svc.resolve("sb-1", "logger")
    assert result.name == "logger"
    assert result.implementation == "ConsoleLogger"


def test_singleton_cached():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "db", "PostgresDB", Lifetime.SINGLETON)
    r1 = svc.resolve("sb-1", "db")
    r2 = svc.resolve("sb-1", "db")
    assert r1.instance_id == r2.instance_id
    assert r2.from_cache is True


def test_transient_new_instance():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "handler", "RequestHandler", Lifetime.TRANSIENT)
    r1 = svc.resolve("sb-1", "handler")
    r2 = svc.resolve("sb-1", "handler")
    assert r1.instance_id != r2.instance_id


def test_dependency_resolution():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "db", "PostgresDB")
    svc.register("sb-1", "repo", "UserRepo", dependencies=["db"])
    result = svc.resolve("sb-1", "repo")
    assert result.name == "repo"


def test_circular_dependency_detected():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "a", "A", dependencies=["b"])
    svc.register("sb-1", "b", "B", dependencies=["a"])
    result = svc.resolve("sb-1", "a")
    assert isinstance(result, dict)
    assert "Circular" in result["error"]


def test_missing_dependency():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "svc", "MySvc", dependencies=["missing"])
    result = svc.resolve("sb-1", "svc")
    assert isinstance(result, dict)
    assert "not registered" in result["error"]


def test_find_by_tag():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "cache", "RedisCache", tags=["infra"])
    svc.register("sb-1", "db", "PostgresDB", tags=["infra"])
    svc.register("sb-1", "auth", "AuthService", tags=["security"])
    results = svc.find_by_tag("sb-1", "infra")
    assert set(results) == {"cache", "db"}


def test_dependency_graph():
    svc = SandboxDependencyInjectionService()
    svc.register("sb-1", "db", "DB")
    svc.register("sb-1", "repo", "Repo", dependencies=["db"])
    svc.register("sb-1", "svc", "Svc", dependencies=["repo", "db"])
    graph = svc.get_dependency_graph("sb-1")
    assert graph["svc"] == ["repo", "db"]
    assert graph["db"] == []
