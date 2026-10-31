from app.services.app_marketplace_extension_starter_template import (
    StarterTemplateService, TemplateCategory,
)


def test_register_and_search():
    svc = StarterTemplateService()
    svc.register_template("Slack Bot", "Build a Slack bot", TemplateCategory.INTEGRATION,
                          "node20", tags=["slack", "bot"])
    results = svc.search("slack")
    assert len(results) == 1
    assert results[0].name == "Slack Bot"


def test_instantiate():
    svc = StarterTemplateService()
    tpl = svc.register_template("API Connector", "Connect to APIs",
                                TemplateCategory.INTEGRATION, "node20",
                                variables=[{"name": "api_name", "label": "API Name"}],
                                files={
                                    "src/{{api_name}}.ts": "// {{api_name}} connector",
                                    "README.md": "# {{api_name}} Connector",
                                })
    result = svc.instantiate(tpl.template_id, {"api_name": "GitHub"})
    assert "src/GitHub.ts" in result
    assert "// GitHub connector" in result["src/GitHub.ts"]
    assert "# GitHub Connector" in result["README.md"]


def test_missing_required_variable():
    svc = StarterTemplateService()
    tpl = svc.register_template("T", "D", TemplateCategory.AUTOMATION, "python3.12",
                                variables=[{"name": "name", "required": True}])
    result = svc.instantiate(tpl.template_id, {})
    assert "error" in result


def test_default_value():
    svc = StarterTemplateService()
    tpl = svc.register_template("T", "D", TemplateCategory.ANALYTICS, "node20",
                                variables=[{"name": "port", "default": "3000"}],
                                files={"config.json": '{"port": {{port}}}' })
    result = svc.instantiate(tpl.template_id, {})
    assert '"port": 3000' in result["config.json"]


def test_category_filter():
    svc = StarterTemplateService()
    svc.register_template("A", "D", TemplateCategory.WEBHOOK, "node20")
    svc.register_template("B", "D", TemplateCategory.ANALYTICS, "node20")
    results = svc.search(category=TemplateCategory.WEBHOOK)
    assert len(results) == 1


def test_popularity_tracking():
    svc = StarterTemplateService()
    tpl = svc.register_template("Pop", "D", TemplateCategory.UI_WIDGET, "node20",
                                files={"index.ts": "export default {}"})
    svc.instantiate(tpl.template_id, {})
    svc.instantiate(tpl.template_id, {})
    assert tpl.popularity == 2
    popular = svc.get_popular(1)
    assert popular[0].template_id == tpl.template_id
