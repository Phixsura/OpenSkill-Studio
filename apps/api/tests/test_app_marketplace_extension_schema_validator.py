from app.services.app_marketplace_extension_schema_validator import SchemaValidatorService


def test_type_check():
    v = SchemaValidatorService()
    assert v.validate("hello", {"type": "string"}) == []
    assert len(v.validate(123, {"type": "string"})) == 1
    assert v.validate(42, {"type": "integer"}) == []
    assert v.validate(True, {"type": "boolean"}) == []


def test_bool_not_integer():
    v = SchemaValidatorService()
    errors = v.validate(True, {"type": "integer"})
    assert len(errors) == 1


def test_required_fields():
    v = SchemaValidatorService()
    schema = {"type": "object", "required": ["name", "email"],
              "properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
    errors = v.validate({"name": "Alice"}, schema)
    assert any("email" in e.path and "Required" in e.message for e in errors)


def test_string_constraints():
    v = SchemaValidatorService()
    schema = {"type": "string", "minLength": 3, "maxLength": 10}
    assert v.validate("hi", schema) != []  # too short
    assert v.validate("hello", schema) == []
    assert v.validate("x" * 11, schema) != []  # too long


def test_pattern():
    v = SchemaValidatorService()
    schema = {"type": "string", "pattern": r"^[a-z]+@[a-z]+\.[a-z]+$"}
    assert v.validate("test@example.com", schema) == []
    assert v.validate("not-an-email", schema) != []


def test_enum():
    v = SchemaValidatorService()
    schema = {"type": "string", "enum": ["active", "inactive"]}
    assert v.validate("active", schema) == []
    assert v.validate("deleted", schema) != []


def test_number_range():
    v = SchemaValidatorService()
    schema = {"type": "integer", "minimum": 0, "maximum": 100}
    assert v.validate(50, schema) == []
    assert v.validate(-1, schema) != []
    assert v.validate(101, schema) != []


def test_nested_object():
    v = SchemaValidatorService()
    schema = {"type": "object", "properties": {
        "address": {"type": "object", "required": ["city"], "properties": {
            "city": {"type": "string"},
            "zip": {"type": "string", "pattern": r"^\d{5}$"},
        }}
    }}
    errors = v.validate({"address": {"zip": "1234"}}, schema)
    assert any("city" in e.path for e in errors)
    assert any("pattern" in e.message for e in errors)


def test_array_validation():
    v = SchemaValidatorService()
    schema = {"type": "array", "minItems": 1, "maxItems": 3,
              "items": {"type": "string", "minLength": 1}}
    assert v.validate(["a", "b"], schema) == []
    assert v.validate([], schema) != []  # too few
    assert v.validate(["a", "b", "c", "d"], schema) != []  # too many
    errors = v.validate(["a", ""], schema)
    assert any("[1]" in e.path for e in errors)  # empty string at index 1


def test_nullable():
    v = SchemaValidatorService()
    assert v.validate(None, {"type": "string", "nullable": True}) == []
    assert v.validate(None, {"type": "string"}) != []


def test_no_additional_properties():
    v = SchemaValidatorService()
    schema = {"type": "object", "properties": {"name": {"type": "string"}},
              "additionalProperties": False}
    errors = v.validate({"name": "ok", "extra": "bad"}, schema)
    assert any("Additional" in e.message for e in errors)
