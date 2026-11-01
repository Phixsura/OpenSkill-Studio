from app.services.app_marketplace_schema_registry import SchemaRegistry


USER_SCHEMA = {
    "required": ["name", "email"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "age": {"type": "integer"},
    },
}


def test_register_and_get():
    sr = SchemaRegistry()
    v1 = sr.register("user", USER_SCHEMA)
    assert v1.version == 1
    latest = sr.get_latest("user")
    assert latest is not None
    assert latest.version == 1


def test_versioning():
    sr = SchemaRegistry()
    sr.register("event", {"properties": {"type": {"type": "string"}}})
    sr.register("event", {"properties": {"type": {"type": "string"}, "data": {"type": "object"}}})
    assert len(sr.list_versions("event")) == 2
    assert sr.get_latest("event").version == 2


def test_validate_success():
    sr = SchemaRegistry()
    sr.register("user", USER_SCHEMA)
    ok, errors = sr.validate("user", {"name": "Alice", "email": "a@b.com", "age": 30})
    assert ok is True


def test_validate_missing_required():
    sr = SchemaRegistry()
    sr.register("user", USER_SCHEMA)
    ok, errors = sr.validate("user", {"name": "Alice"})
    assert ok is False
    assert any("email" in e for e in errors)


def test_validate_wrong_type():
    sr = SchemaRegistry()
    sr.register("user", USER_SCHEMA)
    ok, errors = sr.validate("user", {"name": "Alice", "email": "a@b.com", "age": "thirty"})
    assert ok is False
    assert any("integer" in e for e in errors)


def test_compatibility_ok():
    sr = SchemaRegistry()
    sr.register("item", {"required": ["id"], "properties": {"id": {"type": "string"}}})
    # Adding optional field is backward-compatible
    ok, issues = sr.check_compatibility("item", {
        "required": ["id"],
        "properties": {"id": {"type": "string"}, "description": {"type": "string"}},
    })
    assert ok is True


def test_compatibility_breaking():
    sr = SchemaRegistry()
    sr.register("item", {"required": ["id"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}}})
    # Adding new required field + removing existing = breaking
    ok, issues = sr.check_compatibility("item", {
        "required": ["id", "category"],
        "properties": {"id": {"type": "string"}, "category": {"type": "string"}},
    })
    assert ok is False
    assert any("breaking" in i.lower() for i in issues)


def test_deprecate():
    sr = SchemaRegistry()
    sr.register("old", {"properties": {}})
    sr.register("old", {"properties": {"v": {"type": "integer"}}})
    sr.deprecate_version("old", 1)
    assert sr.get_version("old", 1).deprecated is True
    assert sr.get_latest("old").version == 2
