from app.services.app_marketplace_app_app_sdk_version import get_sdk_info, list_sdks

def test_typescript():
    r = get_sdk_info(language="typescript")
    assert r["latest"] == "3.2.0"
    assert "npm" in r["install"]

def test_unknown():
    r = get_sdk_info(language="rust")
    assert "error" in r

def test_list():
    r = list_sdks()
    assert r["total"] == 4
