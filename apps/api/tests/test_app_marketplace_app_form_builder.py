from app.services.app_marketplace_app_form_builder import create_form_schema, validate_form_data

def test_schema():
    fields = [
        {"name": "app_name", "type": "text", "required": True},
        {"name": "category", "type": "select", "options": ["tools", "design"]},
        {"name": "agree", "type": "checkbox"},
    ]
    r = create_form_schema(title="Create App", fields=fields)
    assert r["valid"]
    assert r["field_count"] == 3

def test_invalid_type():
    r = create_form_schema(title="X", fields=[{"name": "x", "type": "rainbow"}])
    assert not r["valid"]

def test_validate():
    schema = {"fields": [{"name": "email", "type": "email", "required": True}]}
    r = validate_form_data(schema=schema, data={"email": "alice@example.com"})
    assert r["valid"]

def test_validate_fail():
    schema = {"fields": [{"name": "name", "type": "text", "required": True}]}
    r = validate_form_data(schema=schema, data={})
    assert not r["valid"]
