from app.services.app_marketplace_extension_plugin_loader import PluginLoaderService


def test_register():
    pl = PluginLoaderService()
    pl.register("auth", "1.0")
    pl.register("logging", "1.0")
    assert len(pl.get_status()) == 2


def test_dependency_order():
    pl = PluginLoaderService()
    pl.register("db", "1.0")
    pl.register("cache", "1.0")
    pl.register("api", "1.0", dependencies=["db", "cache"])
    order = pl.resolve_order()
    assert order.index("db") < order.index("api")
    assert order.index("cache") < order.index("api")


def test_load_all():
    pl = PluginLoaderService()
    loaded = []
    pl.register("base", "1.0", init_fn=lambda ctx: loaded.append("base"))
    pl.register("ext", "1.0", dependencies=["base"],
                init_fn=lambda ctx: loaded.append("ext"))
    pl.load_all()
    assert loaded == ["base", "ext"]


def test_lifecycle():
    pl = PluginLoaderService()
    log = []
    pl.register("svc", "1.0",
                init_fn=lambda ctx: log.append("init"),
                start_fn=lambda ctx: log.append("start"),
                stop_fn=lambda ctx: log.append("stop"))
    pl.load_all()
    pl.start("svc")
    pl.stop("svc")
    assert log == ["init", "start", "stop"]


def test_hooks():
    pl = PluginLoaderService()
    pl.register("auth", "1.0",
                hooks={"on_request": lambda req: {"user": "alice"}})
    pl.load_all()
    results = pl.call_hook("on_request", {"path": "/api"})
    assert results[0]["result"]["user"] == "alice"


def test_hook_multiple_plugins():
    pl = PluginLoaderService()
    pl.register("logger", "1.0",
                hooks={"on_request": lambda r: "logged"})
    pl.register("metrics", "1.0",
                hooks={"on_request": lambda r: "measured"})
    pl.load_all()
    results = pl.call_hook("on_request", {})
    assert len(results) == 2


def test_conflict_detection():
    pl = PluginLoaderService()
    pl.register("a", "1.0", hooks={"render": lambda: "a"})
    pl.register("b", "1.0", hooks={"render": lambda: "b"})
    conflicts = pl.detect_conflicts()
    assert "render" in conflicts


def test_circular_dependency():
    pl = PluginLoaderService()
    pl.register("a", "1.0", dependencies=["b"])
    pl.register("b", "1.0", dependencies=["a"])
    try:
        pl.resolve_order()
        assert False
    except ValueError:
        pass


def test_init_error():
    pl = PluginLoaderService()
    pl.register("bad", "1.0",
                init_fn=lambda ctx: (_ for _ in ()).throw(RuntimeError("fail")))
    results = pl.load_all()
    assert results[0]["status"] == "error"


def test_hook_only_active():
    pl = PluginLoaderService()
    pl.register("inactive", "1.0",
                hooks={"hook": lambda: "should not run"})
    # Not loaded → hook should not fire
    results = pl.call_hook("hook")
    assert len(results) == 0
