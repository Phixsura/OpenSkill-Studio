from app.services.app_marketplace_api_versioning import (
    APIVersionManager, VersionStatus,
)


def _setup() -> APIVersionManager:
    vm = APIVersionManager()
    vm.register_version("v1", VersionStatus.SUPPORTED, "2025-01-01",
                        breaking_changes=["Initial release"])
    vm.register_version("v2", VersionStatus.CURRENT, "2026-06-01",
                        changelog="Major rewrite",
                        breaking_changes=["Renamed /apps to /extensions", "Auth header changed"])
    return vm


def test_current_version():
    vm = _setup()
    assert vm.get_current() == "v2"


def test_negotiate_current():
    vm = _setup()
    ver, headers = vm.negotiate("v2")
    assert ver == "v2"
    assert headers["X-API-Version"] == "v2"


def test_negotiate_deprecated():
    vm = _setup()
    vm.deprecate("v1", sunset_at="2027-01-01")
    ver, headers = vm.negotiate("v1")
    assert ver == "v1"  # still served
    assert "Deprecation" in headers.get("X-Deprecation-Notice", "")
    assert headers["X-Sunset-Date"] == "2027-01-01"


def test_negotiate_sunset():
    vm = _setup()
    vm.deprecate("v1")
    vm.sunset("v1")
    ver, headers = vm.negotiate("v1")
    assert ver == "v2"  # falls back to current
    assert "sunset" in headers.get("X-Sunset-Notice", "").lower()


def test_negotiate_unknown():
    vm = _setup()
    ver, headers = vm.negotiate("v99")
    assert ver == "v2"
    assert "Fallback" in headers.get("X-Fallback", "")


def test_list_versions():
    vm = _setup()
    vm.deprecate("v1")
    vm.sunset("v1")
    active = vm.list_versions(include_sunset=False)
    assert all(v.status != VersionStatus.SUNSET for v in active)
    all_vers = vm.list_versions(include_sunset=True)
    assert len(all_vers) == 2


def test_migration_guide():
    vm = _setup()
    guide = vm.get_migration_guide("v1", "v2")
    assert len(guide["breaking_changes"]) >= 2
    assert "Renamed" in guide["breaking_changes"][0]
