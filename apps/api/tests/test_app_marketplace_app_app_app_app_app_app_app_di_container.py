from app.services.app_marketplace_app_app_app_app_app_app_app_di_container import DIContainer

def test_transient():
    di = DIContainer()
    di.register("db", lambda: {"conn": "new"})
    a = di.resolve("db")
    b = di.resolve("db")
    assert a is not b  # different instances

def test_singleton():
    di = DIContainer()
    di.register("cache", lambda: {"pool": "shared"}, singleton=True)
    a = di.resolve("cache")
    b = di.resolve("cache")
    assert a is b  # same instance

def test_missing():
    di = DIContainer()
    assert not di.has("missing")
    try:
        di.resolve("missing")
        assert False
    except KeyError:
        pass

def test_stats():
    di = DIContainer()
    di.register("a", lambda: 1)
    di.register("b", lambda: 2, singleton=True)
    di.resolve("b")
    s = di.stats()
    assert s["registered"] == 2
    assert s["singletons_created"] == 1
