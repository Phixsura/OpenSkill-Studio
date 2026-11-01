from app.services.app_marketplace_extension_config_watcher import ConfigWatcherService


def test_load_and_get():
    cw = ConfigWatcherService()
    cw.load({"debug": True, "port": 8080})
    assert cw.get("debug") is True
    assert cw.get("port") == 8080
    assert cw.get("missing", "default") == "default"


def test_update():
    cw = ConfigWatcherService()
    cw.load({"port": 8080})
    result = cw.update({"port": 9090})
    assert "port" in result["applied"]
    assert cw.get("port") == 9090


def test_no_change_skipped():
    cw = ConfigWatcherService()
    cw.load({"x": 1})
    result = cw.update({"x": 1})
    assert result["applied"] == []


def test_validation():
    cw = ConfigWatcherService()
    cw.load({"port": 8080})
    cw.add_validator("port", lambda v: isinstance(v, int) and 1024 <= v <= 65535)
    result = cw.update({"port": 80})  # below 1024
    assert "port" in [r["key"] for r in result["rejected"]]
    assert cw.get("port") == 8080  # unchanged


def test_listener():
    cw = ConfigWatcherService()
    cw.load({"mode": "dev"})
    changes = []
    cw.on_change("mode", lambda k, old, new: changes.append((old, new)))
    cw.update({"mode": "prod"})
    assert changes == [("dev", "prod")]


def test_wildcard_listener():
    cw = ConfigWatcherService()
    cw.load({"a": 1, "b": 2})
    all_changes = []
    cw.on_change("*", lambda k, old, new: all_changes.append(k))
    cw.update({"a": 10, "b": 20})
    assert set(all_changes) == {"a", "b"}


def test_rollback():
    cw = ConfigWatcherService()
    cw.load({"feature": False})
    cw.update({"feature": True})
    assert cw.get("feature") is True
    cw.rollback("feature")
    assert cw.get("feature") is False


def test_diff():
    cw = ConfigWatcherService()
    cw.load({"a": 1, "b": 2, "c": 3})
    diff = cw.diff({"a": 1, "b": 99, "d": 4})
    types = {d["key"]: d["type"] for d in diff}
    assert types["b"] == "changed"
    assert types["c"] == "removed"
    assert types["d"] == "added"


def test_history():
    cw = ConfigWatcherService()
    cw.load({"x": 0})
    cw.update({"x": 1})
    cw.update({"x": 2})
    history = cw.get_history("x")
    assert len(history) == 2
    assert history[-1]["new"] == 2
