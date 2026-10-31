from app.services.app_marketplace_extension_developer_settings import DeveloperSettingsService


def test_get_or_create():
    svc = DeveloperSettingsService()
    s = svc.get_or_create("dev-1")
    assert s.default_runtime == "node20"
    assert s.theme == "system"


def test_update():
    svc = DeveloperSettingsService()
    svc.update("dev-1", display_name="Alice", theme="dark", auto_deploy=True)
    s = svc.get_settings("dev-1")
    assert s["display_name"] == "Alice"
    assert s["theme"] == "dark"
    assert s["auto_deploy"] is True


def test_invalid_runtime():
    svc = DeveloperSettingsService()
    result = svc.update("dev-1", default_runtime="ruby")
    assert isinstance(result, dict) and "error" in result


def test_invalid_theme():
    svc = DeveloperSettingsService()
    result = svc.update("dev-1", theme="neon")
    assert isinstance(result, dict) and "error" in result


def test_reset():
    svc = DeveloperSettingsService()
    svc.update("dev-1", theme="dark", auto_deploy=True)
    s = svc.reset_defaults("dev-1")
    assert s.theme == "system"
    assert s.auto_deploy is False
