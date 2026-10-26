from app.services.app_marketplace_extension_webhook_templates import WebhookTemplateService


def test_list_templates():
    svc = WebhookTemplateService()
    templates = svc.list_templates()
    assert len(templates) >= 5


def test_filter_by_provider():
    svc = WebhookTemplateService()
    github = svc.list_templates(provider="github")
    assert all(t.provider == "github" for t in github)


def test_get_providers():
    svc = WebhookTemplateService()
    providers = svc.get_providers()
    assert "github" in providers
    assert "slack" in providers


def test_search():
    svc = WebhookTemplateService()
    results = svc.search("slack")
    assert len(results) >= 1
    assert results[0].provider == "slack"


def test_instantiate():
    svc = WebhookTemplateService()
    result = svc.instantiate("github-push", {"owner": "acme", "repo": "app"})
    assert result is not None
    assert "acme" in result["url"]
    assert "app" in result["url"]
    assert "push" in result["events"]


def test_instantiate_unknown():
    svc = WebhookTemplateService()
    assert svc.instantiate("nonexistent", {}) is None
