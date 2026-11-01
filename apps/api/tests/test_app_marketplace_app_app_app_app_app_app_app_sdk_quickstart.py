from app.services.app_marketplace_app_app_app_app_app_app_app_sdk_quickstart import get_quickstart, list_languages

def test_quickstart():
    r = get_quickstart("typescript")
    assert "npm install" in r["install"]
    assert "OpenSkill" in r["code"]
    assert r["has_install"]

def test_curl():
    r = get_quickstart("curl")
    assert not r["has_install"]
    assert "curl" in r["code"]

def test_list():
    langs = list_languages()
    assert len(langs) == 4
    assert any(l["language"] == "python" for l in langs)

def test_unknown():
    r = get_quickstart("ruby")
    assert "error" in r
