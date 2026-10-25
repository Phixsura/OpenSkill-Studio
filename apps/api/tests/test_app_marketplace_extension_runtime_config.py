from app.services.app_marketplace_extension_runtime_config import RuntimeConfigService


def test_set_and_get():
    rc = RuntimeConfigService()
    rc.set_initial("ext-1", "org-1", {"theme": "dark", "timeout": 30})
    config = rc.get_config("ext-1", "org-1")
    assert config["theme"] == "dark"


def test_update():
    rc = RuntimeConfigService()
    rc.set_initial("ext-2", "org-1", {"mode": "basic"})
    ok, _ = rc.update("ext-2", "org-1", "mode", "advanced")
    assert ok
    assert rc.get_config("ext-2", "org-1")["mode"] == "advanced"


def test_validation():
    rc = RuntimeConfigService()
    rc.set_initial("ext-3", "org-1", {"port": 8080})
    rc.register_validator("port", lambda v: (isinstance(v, int) and 1024 <= v <= 65535, "Must be int 1024-65535"))
    ok, msg = rc.update("ext-3", "org-1", "port", 80)
    assert ok is False
    assert "Validation" in msg
    ok2, _ = rc.update("ext-3", "org-1", "port", 3000)
    assert ok2 is True


def test_batch_update():
    rc = RuntimeConfigService()
    rc.set_initial("ext-4", "org-1", {"a": 1, "b": 2})
    ok, errors = rc.batch_update("ext-4", "org-1", {"a": 10, "b": 20})
    assert ok is True
    config = rc.get_config("ext-4", "org-1")
    assert config["a"] == 10 and config["b"] == 20


def test_rollback():
    rc = RuntimeConfigService()
    rc.set_initial("ext-5", "org-1", {"color": "blue"})
    rc.update("ext-5", "org-1", "color", "red")
    ok, msg = rc.rollback_last("ext-5", "org-1")
    assert ok is True
    assert rc.get_config("ext-5", "org-1")["color"] == "blue"


def test_history():
    rc = RuntimeConfigService()
    rc.set_initial("ext-6", "org-1", {"x": 0})
    rc.update("ext-6", "org-1", "x", 1)
    rc.update("ext-6", "org-1", "x", 2)
    history = rc.get_history("ext-6", "org-1")
    assert len(history) == 2
    assert history[0].old_value == 0
    assert history[1].new_value == 2


def test_isolation():
    rc = RuntimeConfigService()
    rc.set_initial("ext-7", "org-a", {"val": "a"})
    rc.set_initial("ext-7", "org-b", {"val": "b"})
    rc.update("ext-7", "org-a", "val", "updated")
    assert rc.get_config("ext-7", "org-b")["val"] == "b"
