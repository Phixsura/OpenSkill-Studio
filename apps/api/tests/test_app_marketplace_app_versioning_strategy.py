from app.services.app_marketplace_app_versioning_strategy import parse_semver, suggest_next_version, check_version_order, detect_breaking_change

def test_parse():
    v = parse_semver("1.2.3")
    assert v == {"major": 1, "minor": 2, "patch": 3, "prerelease": None}

def test_parse_pre():
    v = parse_semver("2.0.0-beta.1")
    assert v["prerelease"] == "beta.1"

def test_parse_invalid():
    assert parse_semver("not-a-version") is None

def test_next_major():
    r = suggest_next_version(current="1.2.3", change_type="major")
    assert r["version"] == "2.0.0"

def test_next_minor():
    r = suggest_next_version(current="1.2.3", change_type="minor")
    assert r["version"] == "1.3.0"

def test_next_patch():
    r = suggest_next_version(current="1.2.3", change_type="patch")
    assert r["version"] == "1.2.4"

def test_order_valid():
    r = check_version_order(current="1.0.0", proposed="2.0.0")
    assert r["valid"]

def test_order_invalid():
    r = check_version_order(current="2.0.0", proposed="1.0.0")
    assert not r["valid"]

def test_breaking():
    assert detect_breaking_change(old_version="1.0.0", new_version="2.0.0")
    assert not detect_breaking_change(old_version="1.0.0", new_version="1.1.0")
