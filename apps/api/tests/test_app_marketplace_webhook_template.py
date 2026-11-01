from app.services.app_marketplace_webhook_template import get_template, list_templates, render_template

def test_get():
    t = get_template("app.installed")
    assert t["event"] == "app.installed"

def test_get_unknown():
    assert get_template("unknown") is None

def test_list():
    templates = list_templates()
    assert len(templates) >= 4
    assert all("event" in t for t in templates)

def test_render():
    r = render_template(event_type="app.installed", values={"installation_id": "i1", "org_id": "o1", "app_id": "a1", "user_id": "u1"})
    assert r["payload"]["installation_id"] == "i1"
    assert r["payload"]["org_id"] == "o1"

def test_render_unknown():
    assert render_template(event_type="unknown", values={}) is None
