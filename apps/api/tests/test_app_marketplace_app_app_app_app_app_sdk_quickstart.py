from app.services.app_marketplace_app_app_app_app_app_sdk_quickstart import build_sdk_quickstart

def test_typescript():
    r = build_sdk_quickstart(language="typescript")
    assert r["step_count"] == 5
    assert "npm install" in r["steps"][0]["code"]

def test_python():
    r = build_sdk_quickstart(language="python")
    assert "pip install" in r["steps"][0]["code"]

def test_languages():
    r = build_sdk_quickstart()
    assert "typescript" in r["available_languages"]
    assert "python" in r["available_languages"]
