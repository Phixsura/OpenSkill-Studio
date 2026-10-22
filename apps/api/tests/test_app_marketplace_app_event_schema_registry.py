from app.services.app_marketplace_app_event_schema_registry import register_event_schema, validate_event_payload, list_event_types

def test_register():
    r = register_event_schema(event_type="app.installed", schema={"properties": {"app_id": {"type": "string"}}})
    assert r["event_type"] == "app.installed"

def test_bad_type():
    r = register_event_schema(event_type="nonamespace", schema={"properties": {}})
    assert r["error"]

def test_validate_ok():
    schema = {"properties": {"app_id": {"type": "string"}}, "required": ["app_id"]}
    r = validate_event_payload(payload={"app_id": "a1"}, schema=schema)
    assert r["valid"]

def test_validate_missing():
    schema = {"properties": {}, "required": ["app_id"]}
    r = validate_event_payload(payload={}, schema=schema)
    assert not r["valid"]

def test_list():
    schemas = [{"event_type": "app.installed", "version": 1, "schema": {"properties": {"a": {}}}}]
    r = list_event_types(schemas=schemas)
    assert r[0]["field_count"] == 1
