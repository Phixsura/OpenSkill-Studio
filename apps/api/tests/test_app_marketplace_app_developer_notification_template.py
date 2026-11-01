from app.services.app_marketplace_app_developer_notification_template import render_notification, list_templates

def test_render():
    r = render_notification(template_id="install", params={"app_name": "MyApp", "org_name": "Acme"})
    assert "MyApp" in r["body"]
    assert "Acme" in r["body"]

def test_unknown():
    assert render_notification(template_id="nope", params={}) is None

def test_list():
    t = list_templates()
    assert len(t) >= 6
    assert any(x["id"] == "error_spike" for x in t)
