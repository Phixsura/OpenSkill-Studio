from app.services.app_marketplace_config_store import ConfigStore


def test_register_set_get():
    store = ConfigStore()
    store.register_schema("ext-1", {
        "api_url": {"type": "string", "required": True},
        "timeout": {"type": "int"},
    }, defaults={"timeout": 30})
    ok, errors = store.set_config("org-1", "ext-1", {"api_url": "https://api.test"})
    assert ok is True
    config = store.get_config("org-1", "ext-1")
    assert config["api_url"] == "https://api.test"
    assert config["timeout"] == 30  # default


def test_validation_errors():
    store = ConfigStore()
    store.register_schema("ext-2", {
        "name": {"type": "string", "required": True},
        "count": {"type": "int"},
    })
    ok, errors = store.set_config("org-2", "ext-2", {"count": "not_int"})
    assert ok is False
    assert any("Missing required" in e for e in errors)
    assert any("expected int" in e for e in errors)


def test_mask_secrets():
    store = ConfigStore()
    store.register_schema("ext-3", {
        "token": {"type": "string", "secret": True},
        "name": {"type": "string"},
    })
    store.set_config("org-3", "ext-3", {"token": "super_secret", "name": "visible"})
    masked = store.get_config("org-3", "ext-3", mask_secrets=True)
    assert masked["token"] == "***"
    assert masked["name"] == "visible"
    unmasked = store.get_config("org-3", "ext-3", mask_secrets=False)
    assert unmasked["token"] == "super_secret"


def test_delete_config():
    store = ConfigStore()
    store.set_config("org-4", "ext-4", {"key": "val"})
    assert store.delete_config("org-4", "ext-4") is True
    assert store.get_config("org-4", "ext-4") == {}


def test_list_configured():
    store = ConfigStore()
    store.set_config("org-5", "ext-a", {"x": 1})
    store.set_config("org-5", "ext-b", {"y": 2})
    configured = store.list_configured("org-5")
    assert "ext-a" in configured
    assert "ext-b" in configured
