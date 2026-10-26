from app.services.app_marketplace_extension_sdk_version_manager import (
    SDKVersionManagerService, SDKStatus,
)


def _setup():
    svc = SDKVersionManagerService()
    svc.register_release("1.0.0", SDKStatus.STABLE, "2.0.0", "3.0.0")
    svc.register_release("2.0.0", SDKStatus.STABLE, "3.0.0", "4.0.0")
    svc.register_release("3.0.0", SDKStatus.BETA, "4.0.0", "5.0.0")
    return svc


def test_register_and_list():
    svc = _setup()
    releases = svc.list_releases()
    assert len(releases) == 3
    assert releases[0].version == "3.0.0"  # sorted desc


def test_compatibility_ok():
    svc = _setup()
    r = svc.check_compatibility("2.0.0", "3.5.0")
    assert r["compatible"] is True


def test_platform_too_old():
    svc = _setup()
    r = svc.check_compatibility("2.0.0", "2.0.0")
    assert r["compatible"] is False
    assert "too old" in r["reason"]


def test_platform_too_new():
    svc = _setup()
    r = svc.check_compatibility("1.0.0", "4.0.0")
    assert r["compatible"] is False
    assert "too new" in r["reason"]


def test_deprecation():
    svc = _setup()
    svc.deprecate("1.0.0", "Upgrade to 2.0.0")
    r = svc.check_compatibility("1.0.0", "2.5.0")
    assert r["compatible"] is True
    assert len(r["warnings"]) > 0


def test_recommend_version():
    svc = _setup()
    rec = svc.recommend_version("3.5.0")
    assert rec == "2.0.0"  # stable, compatible


def test_upgrade_path():
    svc = _setup()
    svc.add_upgrade_path("1.0.0", "2.0.0",
                         ["Update imports", "Run migration script"],
                         has_breaking=True)
    path = svc.get_upgrade_path("1.0.0", "2.0.0")
    assert path is not None
    assert path.has_breaking_changes is True
    assert len(path.steps) == 2


def test_eol_incompatible():
    svc = _setup()
    svc._releases["1.0.0"].status = SDKStatus.EOL
    r = svc.check_compatibility("1.0.0", "2.5.0")
    assert r["compatible"] is False
    assert "end-of-life" in r["reason"]
