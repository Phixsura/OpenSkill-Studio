from app.services.app_marketplace_extension_sandbox_plugin_registry import (
    SandboxPluginRegistryService,
)
import pytest


def test_register_and_list():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "chart-plugin", "1.0", tags=["ui", "chart"])
    assert len(svc.list_plugins("sb-1")) == 1


def test_search():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "chart-plugin", "1.0", tags=["ui"])
    svc.register("sb-1", "auth-plugin", "2.0", tags=["security"])
    results = svc.search("sb-1", "chart")
    assert len(results) == 1


def test_dependency_check():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "core", "1.0")
    svc.register("sb-1", "ui", "1.0", dependencies=["core"])
    assert svc.check_deps("sb-1", "ui")["satisfied"] is True


def test_missing_dependency():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "ui", "1.0", dependencies=["core"])
    deps = svc.check_deps("sb-1", "ui")
    assert deps["satisfied"] is False
    assert "core" in deps["missing"]


def test_cant_remove_depended():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "core", "1.0")
    svc.register("sb-1", "ui", "1.0", dependencies=["core"])
    assert svc.unregister("sb-1", "core") is False  # ui depends on it


def test_enable_requires_deps():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "core", "1.0")
    svc.register("sb-1", "ui", "1.0", dependencies=["core"])
    svc.disable("sb-1", "core")
    assert svc.enable("sb-1", "ui") is False


def test_duplicate_rejected():
    svc = SandboxPluginRegistryService()
    svc.register("sb-1", "plug", "1.0")
    with pytest.raises(ValueError):
        svc.register("sb-1", "plug", "2.0")
