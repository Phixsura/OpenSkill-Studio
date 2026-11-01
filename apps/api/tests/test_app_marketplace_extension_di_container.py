from app.services.app_marketplace_extension_di_container import (
    DiContainerService, Lifecycle
)


def test_singleton():
    di = DiContainerService()
    di.register("config", lambda: {"debug": True}, Lifecycle.SINGLETON)
    a = di.resolve("config")
    b = di.resolve("config")
    assert a is b  # same instance


def test_transient():
    di = DiContainerService()
    call_count = [0]
    def factory():
        call_count[0] += 1
        return {"id": call_count[0]}
    di.register("service", factory, Lifecycle.TRANSIENT)
    a = di.resolve("service")
    b = di.resolve("service")
    assert a is not b  # different instances
    assert a["id"] != b["id"]


def test_dependency_injection():
    di = DiContainerService()
    di.register("db", lambda: {"connection": "postgres://..."})
    di.register("repo", lambda db: {"db": db, "type": "user_repo"},
                dependencies=["db"])
    repo = di.resolve("repo")
    assert repo["db"]["connection"] == "postgres://..."


def test_chained_dependencies():
    di = DiContainerService()
    di.register("config", lambda: {"url": "http://api"})
    di.register("http_client", lambda config: {"base_url": config["url"]},
                dependencies=["config"])
    di.register("user_service", lambda client: {"client": client, "name": "users"},
                dependencies=["http_client"])
    svc = di.resolve("user_service")
    assert svc["client"]["base_url"] == "http://api"


def test_circular_dependency_detected():
    di = DiContainerService()
    di.register("a", lambda b: {"a": True}, dependencies=["b"])
    di.register("b", lambda a: {"b": True}, dependencies=["a"])
    try:
        di.resolve("a")
        assert False
    except ValueError as e:
        assert "Circular" in str(e)


def test_register_instance():
    di = DiContainerService()
    config = {"env": "production"}
    di.register_instance("config", config)
    assert di.resolve("config") is config


def test_scoped_lifecycle():
    di = DiContainerService()
    call_count = [0]
    def factory():
        call_count[0] += 1
        return {"id": call_count[0]}
    di.register("request_ctx", factory, Lifecycle.SCOPED)
    di.create_scope("req-1")
    di.create_scope("req-2")
    a1 = di.resolve("request_ctx", "req-1")
    a2 = di.resolve("request_ctx", "req-1")
    b1 = di.resolve("request_ctx", "req-2")
    assert a1 is a2  # same scope = same instance
    assert a1 is not b1  # different scope = different instance


def test_dispose_scope():
    di = DiContainerService()
    di.register("ctx", lambda: {}, Lifecycle.SCOPED)
    di.create_scope("s1")
    di.resolve("ctx", "s1")
    count = di.dispose_scope("s1")
    assert count == 1


def test_not_registered():
    di = DiContainerService()
    try:
        di.resolve("missing")
        assert False
    except ValueError:
        pass
    assert di.is_registered("missing") is False


def test_registrations_list():
    di = DiContainerService()
    di.register("a", lambda: 1)
    di.register("b", lambda a: 2, dependencies=["a"])
    regs = di.get_registrations()
    assert len(regs) == 2
    b_reg = next(r for r in regs if r["name"] == "b")
    assert b_reg["dependencies"] == ["a"]
