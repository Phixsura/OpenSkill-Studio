from app.services.app_marketplace_extension_dep_injector import DepInjectorService


def test_bind_and_resolve():
    di = DepInjectorService()
    di.bind("greeting", lambda: "Hello, World!")
    assert di.resolve("greeting") == "Hello, World!"


def test_singleton():
    di = DepInjectorService()
    count = [0]
    def factory():
        count[0] += 1
        return {"id": count[0]}
    di.bind("service", factory, singleton=True)
    a = di.resolve("service")
    b = di.resolve("service")
    assert a is b  # same instance
    assert count[0] == 1


def test_transient():
    di = DepInjectorService()
    count = [0]
    def factory():
        count[0] += 1
        return {"id": count[0]}
    di.bind("service", factory, singleton=False)
    a = di.resolve("service")
    b = di.resolve("service")
    assert a is not b
    assert count[0] == 2


def test_bind_instance():
    di = DepInjectorService()
    config = {"debug": True}
    di.bind_instance("config", config)
    assert di.resolve("config") is config


def test_auto_wire():
    di = DepInjectorService()
    di.bind_instance("db", {"connection": "postgres://..."})
    di.bind("repo", lambda db: {"db": db, "type": "user_repo"})
    repo = di.resolve("repo")
    assert repo["db"]["connection"] == "postgres://..."


def test_chained_auto_wire():
    di = DepInjectorService()
    di.bind_instance("config", {"url": "http://api"})
    di.bind("http", lambda config: {"base": config["url"]}, singleton=True)
    di.bind("service", lambda http: {"client": http})
    svc = di.resolve("service")
    assert svc["client"]["base"] == "http://api"


def test_not_bound():
    di = DepInjectorService()
    try:
        di.resolve("missing")
        assert False
    except ValueError:
        pass


def test_module():
    di = DepInjectorService()
    di.module_bind("database", "db_conn", lambda: "pg://localhost", singleton=True)
    di.module_bind("database", "db_pool", lambda: {"size": 5})
    installed = di.install_module("database")
    assert installed == 2
    assert di.resolve("db_conn") == "pg://localhost"


def test_reset():
    di = DepInjectorService()
    di.bind("svc", lambda: {"new": True}, singleton=True)
    di.resolve("svc")
    count = di.reset()
    assert count == 1
    # Re-resolve creates new instance
    svc = di.resolve("svc")
    assert svc is not None


def test_has_binding():
    di = DepInjectorService()
    di.bind("x", lambda: 1)
    assert di.has_binding("x") is True
    assert di.has_binding("y") is False
