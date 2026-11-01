from app.services.app_marketplace_extension_sandbox_config_hot_reload import (
    SandboxConfigHotReloadService,
)


def test_set_and_get():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"theme": "dark", "lang": "en"})
    assert svc.get_config("sb-1") == {"theme": "dark", "lang": "en"}


def test_apply_changes():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"theme": "light"})
    result = svc.apply_changes("sb-1", {"theme": "dark", "debug": "true"})
    assert result.success is True
    assert result.changes_applied == 2
    assert svc.get_config("sb-1")["theme"] == "dark"


def test_validator_rejects():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"port": "3000"})
    svc.register_validator("sb-1", "port", lambda v: v.isdigit())
    result = svc.apply_changes("sb-1", {"port": "not_a_number"})
    assert result.success is False
    assert len(result.errors) == 1
    assert svc.get_config("sb-1")["port"] == "3000"  # unchanged


def test_validator_accepts():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"port": "3000"})
    svc.register_validator("sb-1", "port", lambda v: v.isdigit())
    result = svc.apply_changes("sb-1", {"port": "8080"})
    assert result.success is True
    assert svc.get_config("sb-1")["port"] == "8080"


def test_rollback_change():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"theme": "light"})
    svc.apply_changes("sb-1", {"theme": "dark"})
    history = svc.get_history("sb-1")
    assert svc.rollback_change("sb-1", history[0].change_id) is True
    assert svc.get_config("sb-1")["theme"] == "light"


def test_rollback_all():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {"a": "1", "b": "2"})
    svc.apply_changes("sb-1", {"a": "10", "b": "20"})
    rolled = svc.rollback_all("sb-1")
    assert rolled == 2
    assert svc.get_config("sb-1") == {"a": "1", "b": "2"}


def test_history():
    svc = SandboxConfigHotReloadService()
    svc.set_config("sb-1", {})
    svc.apply_changes("sb-1", {"x": "1"})
    svc.apply_changes("sb-1", {"y": "2"})
    assert len(svc.get_history("sb-1")) == 2


def test_subscribers():
    svc = SandboxConfigHotReloadService()
    svc.subscribe("sb-1", "on_config_update")
    svc.subscribe("sb-1", "refresh_ui")
    assert len(svc.get_subscribers("sb-1")) == 2
