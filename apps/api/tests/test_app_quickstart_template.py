from app.services.app_quickstart_template import generate_quickstart

def test_python():
    q = generate_quickstart(category="connector", app_name="My App", runtime="python3.12")
    assert q["filename"] == "main.py"
    assert "OpenSkillClient" in q["code"]

def test_typescript():
    q = generate_quickstart(category="automation", app_name="Bot", runtime="nodejs20")
    assert q["filename"] == "index.ts"
    assert "OpenSkillClient" in q["code"]

def test_has_category():
    q = generate_quickstart(category="analytics", app_name="X")
    assert q["category"] == "analytics"
