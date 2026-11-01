from app.services.app_marketplace_extension_json_schema_builder import (
    JsonSchemaBuilderService, SchemaBuilder
)


def test_string_builder():
    svc = JsonSchemaBuilderService()
    schema = svc.create().string().min_length(1).max_length(100).build()
    assert schema["type"] == "string"
    assert schema["minLength"] == 1


def test_object_builder():
    svc = JsonSchemaBuilderService()
    schema = (svc.create().object()
              .prop("name", {"type": "string"}, required=True)
              .prop("age", {"type": "integer"})
              .no_additional()
              .build())
    assert "name" in schema["properties"]
    assert "name" in schema["required"]
    assert schema["additionalProperties"] is False


def test_array_builder():
    svc = JsonSchemaBuilderService()
    schema = (svc.create().array()
              .items({"type": "string"})
              .min_items(1).max_items(10).unique()
              .build())
    assert schema["type"] == "array"
    assert schema["uniqueItems"] is True


def test_validate_valid():
    svc = JsonSchemaBuilderService()
    schema = {"type": "object", "required": ["name"],
              "properties": {"name": {"type": "string", "minLength": 1},
                             "age": {"type": "integer", "minimum": 0}}}
    errors = svc.validate({"name": "Alice", "age": 30}, schema)
    assert errors == []


def test_validate_missing_required():
    svc = JsonSchemaBuilderService()
    schema = {"type": "object", "required": ["name"],
              "properties": {"name": {"type": "string"}}}
    errors = svc.validate({}, schema)
    assert any("required" in e for e in errors)


def test_validate_type_mismatch():
    svc = JsonSchemaBuilderService()
    errors = svc.validate("hello", {"type": "integer"})
    assert len(errors) == 1


def test_validate_string_constraints():
    svc = JsonSchemaBuilderService()
    schema = {"type": "string", "minLength": 3, "pattern": r"^[a-z]+$"}
    assert svc.validate("ab", schema) != []  # too short
    assert svc.validate("ABC", schema) != []  # wrong pattern
    assert svc.validate("abc", schema) == []


def test_validate_nested():
    svc = JsonSchemaBuilderService()
    schema = {"type": "object", "properties": {
        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1}}}
    assert svc.validate({"tags": ["a"]}, schema) == []
    assert svc.validate({"tags": []}, schema) != []  # minItems


def test_validate_enum():
    svc = JsonSchemaBuilderService()
    schema = {"type": "string", "enum": ["active", "inactive"]}
    assert svc.validate("active", schema) == []
    assert svc.validate("deleted", schema) != []


def test_docs_generation():
    svc = JsonSchemaBuilderService()
    schema = {"type": "object", "description": "A user",
              "required": ["name"],
              "properties": {
                  "name": {"type": "string", "description": "Full name"},
                  "age": {"type": "integer", "minimum": 0, "maximum": 150}}}
    docs = svc.to_docs(schema)
    assert "name (required)" in docs
    assert "min=0" in docs
