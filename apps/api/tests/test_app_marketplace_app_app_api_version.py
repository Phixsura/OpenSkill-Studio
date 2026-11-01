from app.services.app_marketplace_app_app_api_version import negotiate_version, list_versions

def test_negotiate_v2():
    r = negotiate_version(requested="v2")
    assert r["version"] == "v2"
    assert not r["deprecated"]

def test_negotiate_deprecated():
    r = negotiate_version(requested="v1")
    assert r["deprecated"]
    assert "deprecated" in r["warning"].lower()

def test_default():
    r = negotiate_version()
    assert r["version"] == "v2"

def test_list():
    v = list_versions()
    assert len(v) == 3
