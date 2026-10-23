from app.services.app_marketplace_app_app_getting_started import build_getting_started

def test_typescript():
    r = build_getting_started(language="typescript")
    assert "npm install" in r["install_command"]
    assert len(r["steps"]) == 4
    assert "OpenSkill" in r["code_example"]

def test_python():
    r = build_getting_started(language="python")
    assert "pip install" in r["install_command"]

def test_languages():
    r = build_getting_started()
    assert "typescript" in r["available_languages"]
    assert "python" in r["available_languages"]
