from app.services.app_marketplace_extension_sandbox_data_validator import (
    SandboxDataValidatorService,
)


def test_valid_data():
    svc = SandboxDataValidatorService()
    result = svc.validate(
        {"name": "Alice", "age": 30},
        [{"name": "name", "type": "string"}, {"name": "age", "type": "integer"}],
    )
    assert result["valid"] is True


def test_missing_required():
    svc = SandboxDataValidatorService()
    result = svc.validate({}, [{"name": "email", "type": "string"}])
    assert result["valid"] is False
    assert result["errors"][0]["path"] == "email"


def test_wrong_type():
    svc = SandboxDataValidatorService()
    result = svc.validate({"count": "five"}, [{"name": "count", "type": "integer"}])
    assert result["valid"] is False
    assert "Expected integer" in result["errors"][0]["message"]


def test_range_constraints():
    svc = SandboxDataValidatorService()
    result = svc.validate({"score": 150},
                          [{"name": "score", "type": "integer", "min": 0, "max": 100}])
    assert result["valid"] is False
    assert "<= 100" in result["errors"][0]["message"]


def test_string_length():
    svc = SandboxDataValidatorService()
    result = svc.validate({"bio": "Hi"},
                          [{"name": "bio", "type": "string", "min_length": 10}])
    assert result["valid"] is False


def test_enum():
    svc = SandboxDataValidatorService()
    result = svc.validate({"status": "unknown"},
                          [{"name": "status", "type": "string", "enum": ["active", "inactive"]}])
    assert result["valid"] is False


def test_nested_object():
    svc = SandboxDataValidatorService()
    result = svc.validate(
        {"user": {"name": "Alice", "age": "thirty"}},
        [{"name": "user", "type": "object", "nested": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": "integer"},
        ]}],
    )
    assert result["valid"] is False
    assert result["errors"][0]["path"] == "user.age"


def test_array_items():
    svc = SandboxDataValidatorService()
    result = svc.validate(
        {"scores": [90, "bad", 75]},
        [{"name": "scores", "type": "array", "items_type": "integer"}],
    )
    assert result["valid"] is False
    assert "scores[1]" in result["errors"][0]["path"]


def test_optional_field():
    svc = SandboxDataValidatorService()
    result = svc.validate({}, [{"name": "note", "type": "string", "required": False}])
    assert result["valid"] is True
