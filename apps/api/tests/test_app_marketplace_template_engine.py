from app.services.app_marketplace_template_engine import TemplateEngine, Template, TemplateFile


def test_list_builtin_templates():
    engine = TemplateEngine()
    templates = engine.list_templates()
    assert len(templates) >= 3
    names = [t.template_id for t in templates]
    assert "connector" in names
    assert "widget" in names
    assert "automation" in names


def test_filter_by_category():
    engine = TemplateEngine()
    connectors = engine.list_templates(category="connector")
    assert all(t.category == "connector" for t in connectors)


def test_render_connector():
    engine = TemplateEngine()
    files = engine.render("connector", {
        "extension_name": "Slack",
        "service_name": "Slack API",
        "api_base_url": "https://slack.com/api",
    })
    assert files is not None
    assert len(files) == 4
    connector_file = next(f for f in files if "connector.py" in f.path)
    assert "SlackConnector" in connector_file.content
    assert "https://slack.com/api" in connector_file.content


def test_render_widget():
    engine = TemplateEngine()
    files = engine.render("widget", {
        "extension_name": "Analytics",
        "widget_title": "Traffic Overview",
    })
    assert files is not None
    widget = next(f for f in files if f.path.endswith(".tsx"))
    assert "AnalyticsWidget" in widget.content
    assert "Traffic Overview" in widget.content


def test_missing_variables():
    engine = TemplateEngine()
    result = engine.render("connector", {"extension_name": "Partial"})
    assert result is None


def test_register_custom_template():
    engine = TemplateEngine()
    custom = Template("custom", "Custom", "A custom template", "misc",
                       files=[TemplateFile("main.py", "# {{name}}")],
                       variables=["name"])
    engine.register_template(custom)
    files = engine.render("custom", {"name": "MyExt"})
    assert files is not None
    assert "# MyExt" in files[0].content
