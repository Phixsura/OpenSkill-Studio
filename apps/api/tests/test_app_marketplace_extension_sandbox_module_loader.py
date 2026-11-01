from app.services.app_marketplace_extension_sandbox_module_loader import (
    SandboxModuleLoaderService,
)


def test_builtin_allowed():
    svc = SandboxModuleLoaderService()
    r = svc.can_import("sb-1", "json")
    assert r.allowed is True
    assert r.reason == "Built-in allowed"


def test_blocked_module():
    svc = SandboxModuleLoaderService()
    r = svc.can_import("sb-1", "os")
    assert r.allowed is False
    assert "Blocked" in r.reason


def test_blocked_submodule():
    svc = SandboxModuleLoaderService()
    r = svc.can_import("sb-1", "os.path")
    assert r.allowed is False


def test_unknown_module_denied():
    svc = SandboxModuleLoaderService()
    r = svc.can_import("sb-1", "some_random_package")
    assert r.allowed is False
    assert "allowlist" in r.reason


def test_custom_allowlist():
    svc = SandboxModuleLoaderService()
    svc.add_to_allowlist("sb-1", ["requests", "pandas"])
    r = svc.can_import("sb-1", "requests")
    assert r.allowed is True
    assert "Custom" in r.reason


def test_cannot_override_blocked():
    svc = SandboxModuleLoaderService()
    added = svc.add_to_allowlist("sb-1", ["os", "subprocess", "safe_lib"])
    assert added == 1  # only safe_lib added
    r = svc.can_import("sb-1", "os")
    assert r.allowed is False


def test_import_log():
    svc = SandboxModuleLoaderService()
    svc.can_import("sb-1", "json")
    svc.can_import("sb-1", "os")
    svc.can_import("sb-1", "math")
    log = svc.get_import_log("sb-1")
    assert len(log) == 3
    assert svc.get_blocked_count("sb-1") == 1


def test_get_allowlist():
    svc = SandboxModuleLoaderService()
    svc.add_to_allowlist("sb-1", ["axios"])
    al = svc.get_allowlist("sb-1")
    assert "json" in al["builtin"]
    assert "axios" in al["custom"]
    assert "os" in al["blocked"]
