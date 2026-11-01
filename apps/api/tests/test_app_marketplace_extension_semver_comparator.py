from app.services.app_marketplace_extension_semver_comparator import SemVerComparatorService, SemVer


def test_parse():
    sv = SemVer.parse("1.2.3-beta.1+build.42")
    assert sv is not None
    assert sv.major == 1 and sv.minor == 2 and sv.patch == 3
    assert sv.prerelease == "beta.1"
    assert sv.build == "build.42"


def test_parse_v_prefix():
    sv = SemVer.parse("v2.0.0")
    assert sv is not None and sv.major == 2


def test_parse_invalid():
    assert SemVer.parse("not-a-version") is None
    assert SemVer.parse("1.2") is None


def test_comparison():
    svc = SemVerComparatorService()
    assert svc.compare("1.0.0", "2.0.0") == -1
    assert svc.compare("1.2.0", "1.1.0") == 1
    assert svc.compare("1.0.0", "1.0.0") == 0
    assert svc.compare("1.0.1", "1.0.0") == 1


def test_prerelease_ordering():
    svc = SemVerComparatorService()
    # Pre-release < release
    assert svc.compare("1.0.0-alpha", "1.0.0") == -1
    # alpha < beta
    assert svc.compare("1.0.0-alpha", "1.0.0-beta") == -1
    # Numeric pre-release comparison
    assert svc.compare("1.0.0-rc.1", "1.0.0-rc.2") == -1


def test_sort_versions():
    svc = SemVerComparatorService()
    versions = ["2.0.0", "1.0.0", "1.5.0", "1.0.0-alpha", "3.0.0-beta"]
    sorted_v = svc.sort_versions(versions)
    assert sorted_v == ["1.0.0-alpha", "1.0.0", "1.5.0", "2.0.0", "3.0.0-beta"]


def test_latest():
    svc = SemVerComparatorService()
    versions = ["1.0.0", "2.0.0-rc.1", "1.5.0", "2.0.0"]
    assert svc.latest(versions) == "2.0.0"
    assert svc.latest(versions, include_prerelease=True) == "2.0.0"


def test_latest_only_prerelease():
    svc = SemVerComparatorService()
    versions = ["1.0.0-alpha", "1.0.0-beta"]
    assert svc.latest(versions) is None  # no stable
    assert svc.latest(versions, include_prerelease=True) == "1.0.0-beta"


def test_diff():
    svc = SemVerComparatorService()
    assert svc.diff("1.0.0", "2.0.0") == "major"
    assert svc.diff("1.0.0", "1.1.0") == "minor"
    assert svc.diff("1.0.0", "1.0.1") == "patch"
    assert svc.diff("1.0.0-alpha", "1.0.0-beta") == "prerelease"
    assert svc.diff("1.0.0", "1.0.0") == "equal"


def test_range_or():
    svc = SemVerComparatorService()
    assert svc.satisfies_range("1.5.0", "^1.0.0 || ^2.0.0") is True
    assert svc.satisfies_range("3.0.0", "^1.0.0 || ^2.0.0") is False
