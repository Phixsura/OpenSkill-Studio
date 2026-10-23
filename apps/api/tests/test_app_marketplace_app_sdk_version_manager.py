from app.services.app_marketplace_app_sdk_version_manager import get_sdk_info, check_sdk_compatibility, list_sdks

def test_get():
    r = get_sdk_info(language="typescript")
    assert r["package"] == "@openskill/sdk"

def test_compatible():
    r = check_sdk_compatibility(sdk_version="2.0.0", api_version="v2")
    assert r["compatible"]

def test_incompatible():
    r = check_sdk_compatibility(sdk_version="1.0.0", api_version="v2")
    assert not r["compatible"]

def test_list():
    assert len(list_sdks()) == 4
