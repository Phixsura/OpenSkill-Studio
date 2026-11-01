from app.services.app_marketplace_app_app_webhook_transformer import apply_template, validate_template

def test_transform():
    template = {"event": "{{ type }}", "user": "{{ actor.name }}", "static": "hello"}
    payload = {"type": "install", "actor": {"name": "Alice", "id": "u1"}}
    r = apply_template(template=template, payload=payload)
    assert r["transformed"]["event"] == "install"
    assert r["transformed"]["user"] == "Alice"
    assert r["transformed"]["static"] == "hello"

def test_missing_path():
    r = apply_template(template={"x": "{{ missing.path }}"}, payload={})
    assert r["transformed"]["x"] is None

def test_validate():
    r = validate_template(template={"a": "{{ x.y }}", "b": "{{ z }}"})
    assert r["count"] == 2
    assert "x.y" in r["placeholders"]
