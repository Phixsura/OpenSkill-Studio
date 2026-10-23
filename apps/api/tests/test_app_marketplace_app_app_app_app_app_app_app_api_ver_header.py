from app.services.app_marketplace_app_app_app_app_app_app_app_api_ver_header import parse_api_version, list_versions

def test_url_version():
    r = parse_api_version(url_version="v3")
    assert r["valid"]
    assert r["latest"]
    assert not r["deprecated"]

def test_deprecated():
    r = parse_api_version(url_version="v1")
    assert r["valid"]
    assert r["deprecated"]
    assert r["warning"] is not None

def test_unknown():
    r = parse_api_version(url_version="v99")
    assert not r["valid"]
    assert r["fallback"]

def test_list():
    assert len(list_versions()) == 3
