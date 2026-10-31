from app.services.app_developer_app_template import get_template, list_templates, get_template_by_category

def test_get():
    t = get_template("lms-connector")
    assert t is not None
    assert t["category"] == "connector"

def test_get_unknown():
    assert get_template("nonexist") is None

def test_list():
    templates = list_templates()
    assert len(templates) >= 4
    assert all("id" in t for t in templates)

def test_by_category():
    auto = get_template_by_category("automation")
    assert len(auto) >= 2
    assert all(t["category"] == "automation" for t in auto)

def test_has_secrets():
    t = get_template("slack-notifier")
    assert "secrets" in t
