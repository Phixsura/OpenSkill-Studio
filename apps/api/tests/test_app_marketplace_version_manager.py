from app.services.app_marketplace_version_manager import (
    VersionManager, parse_version,
)


def test_parse_version():
    v = parse_version("1.2.3")
    assert v is not None
    assert v.major == 1 and v.minor == 2 and v.patch == 3
    v2 = parse_version("2.0.0-beta.1")
    assert v2 is not None and v2.prerelease == "beta.1"
    assert parse_version("invalid") is None


def test_version_ordering():
    v1 = parse_version("1.0.0")
    v2 = parse_version("1.1.0")
    v3 = parse_version("2.0.0")
    assert v1 < v2 < v3
    pre = parse_version("1.0.0-alpha")
    rel = parse_version("1.0.0")
    assert pre < rel  # prerelease < release


def test_publish_and_latest():
    vm = VersionManager()
    r1, msg = vm.publish_release("ext-1", "1.0.0", "Initial release")
    assert r1 is not None
    r2, _ = vm.publish_release("ext-1", "1.1.0", "New features")
    assert r2 is not None
    latest = vm.get_latest("ext-1")
    assert str(latest.version) == "1.1.0"


def test_publish_lower_version_fails():
    vm = VersionManager()
    vm.publish_release("ext-2", "2.0.0", "v2")
    r, msg = vm.publish_release("ext-2", "1.0.0", "lower")
    assert r is None
    assert "must be higher" in msg


def test_yank_version():
    vm = VersionManager()
    vm.publish_release("ext-3", "1.0.0", "v1")
    vm.publish_release("ext-3", "1.1.0", "v1.1")
    assert vm.yank_version("ext-3", "1.0.0") is True
    versions = vm.list_versions("ext-3")
    assert all(str(v.version) != "1.0.0" for v in versions)
    all_versions = vm.list_versions("ext-3", include_yanked=True)
    assert len(all_versions) == 2


def test_changelog():
    vm = VersionManager()
    vm.publish_release("ext-4", "1.0.0", "First release with basics")
    vm.publish_release("ext-4", "1.1.0", "Added search feature")
    combined = vm.get_changelog("ext-4")
    assert "First release" in combined
    assert "search feature" in combined
    specific = vm.get_changelog("ext-4", "1.0.0")
    assert "First release" in specific
