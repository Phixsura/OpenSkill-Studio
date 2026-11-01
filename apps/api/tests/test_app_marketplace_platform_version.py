from app.services.app_marketplace_platform_version import get_platform_version, get_platform_changelog, check_api_compatibility

def test_version():
    v = get_platform_version()
    assert v["version"] == "2.1.0"
    assert v["latest"]

def test_changelog():
    c = get_platform_changelog()
    assert len(c) >= 3
    assert c[0]["version"] == "2.1.0"

def test_compatible():
    r = check_api_compatibility(client_version="2.0.0")
    assert r["compatible"]

def test_incompatible():
    r = check_api_compatibility(client_version="1.0.0")
    assert not r["compatible"]
    assert r["upgrade_required"]
