from app.services.app_marketplace_extension_sandbox_api_version import (
    SandboxApiVersionService, VersionStatus,
)


def test_register_and_resolve():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/api/v1/users", "/api/v1/items"])
    result = svc.resolve("sb-1", "v1")
    assert result["resolved"] is True
    assert len(result["endpoints"]) == 2


def test_default_version():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/users"])
    result = svc.resolve("sb-1")
    assert result["version"] == "v1"


def test_deprecation_warning():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/users"])
    svc.deprecate("sb-1", "v1", sunset_date="2025-01-01")
    result = svc.resolve("sb-1", "v1")
    assert result["resolved"] is True
    assert any("deprecated" in w.lower() for w in result["warnings"])


def test_sunset_blocked():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/users"], status=VersionStatus.SUNSET)
    result = svc.resolve("sb-1", "v1")
    assert result["resolved"] is False
    assert "sunset" in result["error"].lower()


def test_multiple_versions():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/users"])
    svc.register_version("sb-1", "v2", ["/users", "/search"])
    svc.set_default("sb-1", "v2")
    result = svc.resolve("sb-1")
    assert result["version"] == "v2"


def test_migration_path():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/users", "/items"])
    svc.register_version("sb-1", "v2", ["/users", "/search", "/analytics"])
    path = svc.get_migration_path("sb-1", "v1", "v2")
    assert "/search" in path["added"]
    assert "/items" in path["removed"]


def test_list_versions():
    svc = SandboxApiVersionService()
    svc.register_version("sb-1", "v1", ["/a"])
    svc.register_version("sb-1", "v2", ["/a", "/b"], status=VersionStatus.BETA)
    listed = svc.list_versions("sb-1")
    assert len(listed) == 2
    assert listed[0]["is_default"] is True
