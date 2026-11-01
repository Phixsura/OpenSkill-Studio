from app.services.app_marketplace_app_app_semver_parser import parse_semver, compare_versions, bump_version

def test_parse():
    r = parse_semver(version="v2.1.3-beta.1+build.42")
    assert r["valid"]
    assert r["major"] == 2
    assert r["minor"] == 1
    assert r["patch"] == 3
    assert r["prerelease"] == "beta.1"
    assert not r["is_stable"]

def test_stable():
    r = parse_semver(version="1.0.0")
    assert r["is_stable"]

def test_compare():
    assert compare_versions(v1="2.0.0", v2="1.9.9")["newer"] == "2.0.0"
    assert compare_versions(v1="1.0.0", v2="1.0.0")["result"] == 0

def test_bump():
    assert bump_version(version="1.2.3", bump="patch")["version"] == "1.2.4"
    assert bump_version(version="1.2.3", bump="minor")["version"] == "1.3.0"
    assert bump_version(version="1.2.3", bump="major")["version"] == "2.0.0"
