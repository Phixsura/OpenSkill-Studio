from app.services.app_marketplace_app_app_template import list_templates, scaffold_from_template

def test_list_all():
    r = list_templates()
    assert r["total"] == 6
    assert len(r["categories"]) >= 3

def test_filter():
    r = list_templates(category="backend")
    assert all(t["category"] == "backend" for t in r["templates"])

def test_scaffold():
    r = scaffold_from_template(template_id="react-widget", app_name="My Widget")
    assert r["project_id"].startswith("proj_")
    assert r["app_name"] == "My Widget"
    assert "React" in r["tech_stack"]

def test_not_found():
    r = scaffold_from_template(template_id="nonexistent", app_name="X")
    assert "error" in r
