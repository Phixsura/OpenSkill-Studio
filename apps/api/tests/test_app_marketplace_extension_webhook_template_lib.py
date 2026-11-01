from app.services.app_marketplace_extension_webhook_template_lib import WebhookTemplateLibService

def test_defaults():
    svc = WebhookTemplateLibService()
    assert len(svc.list_all()) >= 4
    assert svc.get("install") is not None

def test_create_and_render():
    svc = WebhookTemplateLibService()
    svc.create("deploy", "Deployment", "extension.deployed", {"version": "string"})
    result = svc.render("deploy", {"version": "1.0.0"})
    assert result["event"] == "extension.deployed"

def test_search():
    svc = WebhookTemplateLibService()
    results = svc.search("review")
    assert len(results) == 1
