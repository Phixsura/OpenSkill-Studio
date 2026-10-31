from app.services.app_marketplace_app_app_app_app_app_app_app_semver_helper import parse_version, bump, compare

def test_parse():
    r = parse_version("2.3.1")
    assert r["valid"] and r["major"] == 2 and r["minor"] == 3 and r["patch"] == 1
    r2 = parse_version("1.0.0-beta.1")
    assert r2["is_prerelease"]

def test_bump():
    assert bump("1.2.3", "major")["version"] == "2.0.0"
    assert bump("1.2.3", "minor")["version"] == "1.3.0"
    assert bump("1.2.3", "patch")["version"] == "1.2.4"

def test_compare():
    assert compare("2.0.0", "1.9.9")["result"] == 1
    assert compare("1.0.0", "1.0.1")["result"] == -1
    assert compare("3.0.0", "3.0.0")["result"] == 0
