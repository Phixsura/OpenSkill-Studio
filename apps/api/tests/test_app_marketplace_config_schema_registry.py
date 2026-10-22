from app.services.app_marketplace_config_schema_registry import register_schema, validate_config_against_schema, diff_schemas

def test_register():
    r = register_schema(app_id="a1", version=1, schema={"type": "object", "properties": {"url": {"type": "string"}}})
    assert r["registered"]

def test_register_invalid():
    r = register_schema(app_id="a1", version=1, schema={"foo": "bar"})
    assert r["error"]

def test_validate_ok():
    schema = {"properties": {"url": {"type": "string"}}, "required": ["url"]}
    r = validate_config_against_schema(config={"url": "https://x.com"}, schema=schema)
    assert r["valid"]

def test_validate_missing():
    schema = {"properties": {}, "required": ["url"]}
    r = validate_config_against_schema(config={}, schema=schema)
    assert not r["valid"]

def test_validate_wrong_type():
    schema = {"properties": {"count": {"type": "integer"}}, "required": []}
    r = validate_config_against_schema(config={"count": "abc"}, schema=schema)
    assert not r["valid"]

def test_diff():
    d = diff_schemas(old_schema={"properties": {"a": {}, "b": {}}}, new_schema={"properties": {"b": {}, "c": {}}})
    assert d["added"] == ["c"]
    assert d["removed"] == ["a"]
    assert d["breaking"]
