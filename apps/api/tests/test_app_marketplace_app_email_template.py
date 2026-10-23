from app.services.app_marketplace_app_email_template import render_template, list_templates

def test_render():
    template = "Hello {{user_name}}, welcome to {{app_name}}!"
    r = render_template(template=template, variables={"user_name": "Alice", "app_name": "MyApp"})
    assert r["rendered"] == "Hello Alice, welcome to MyApp!"
    assert "user_name" in r["variables_used"]

def test_escaping():
    r = render_template(template="Hi {{name}}", variables={"name": "<script>alert(1)</script>"})
    assert "<script>" not in r["rendered"]
    assert "&lt;script&gt;" in r["rendered"]

def test_missing():
    r = render_template(template="Hi {{name}} from {{company}}", variables={"name": "Bob"})
    assert "error" in r
    assert "company" in r["error"]

def test_list():
    r = list_templates()
    assert r["total"] == 3
