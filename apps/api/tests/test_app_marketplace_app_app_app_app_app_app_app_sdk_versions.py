from app.services.app_marketplace_app_app_app_app_app_app_app_sdk_versions import check_sdk_version, list_sdks

def test_up_to_date():
    r = check_sdk_version("typescript", "3.5.0")
    assert r["up_to_date"]
    assert r["action"] == "none"

def test_outdated():
    r = check_sdk_version("python", "3.2.0")
    assert not r["up_to_date"]
    assert r["supported"]
    assert r["action"] == "update_recommended"

def test_unsupported():
    r = check_sdk_version("go", "2.0.0")
    assert not r["supported"]
    assert r["action"] == "update_required"

def test_list():
    assert len(list_sdks()) == 5
