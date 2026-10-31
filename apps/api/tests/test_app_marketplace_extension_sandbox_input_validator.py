from app.services.app_marketplace_extension_sandbox_input_validator import (
    SandboxInputValidatorService,
)


def test_required():
    svc = SandboxInputValidatorService()
    result = svc.validate({}, [{"field": "name", "rule": "required"}])
    assert not result["valid"]
    assert result["errors"][0]["rule"] == "required"


def test_type_check():
    svc = SandboxInputValidatorService()
    result = svc.validate({"age": "not_int"}, [{"field": "age", "rule": "type", "value": "integer"}])
    assert not result["valid"]


def test_min_max():
    svc = SandboxInputValidatorService()
    r1 = svc.validate({"score": 5}, [{"field": "score", "rule": "min", "value": 10}])
    assert not r1["valid"]
    r2 = svc.validate({"score": 15}, [{"field": "score", "rule": "max", "value": 10}])
    assert not r2["valid"]
    r3 = svc.validate({"score": 10}, [
        {"field": "score", "rule": "min", "value": 0},
        {"field": "score", "rule": "max", "value": 100},
    ])
    assert r3["valid"]


def test_pattern():
    svc = SandboxInputValidatorService()
    r1 = svc.validate({"email": "test@example.com"}, [{"field": "email", "rule": "pattern", "value": r".+@.+\..+"}])
    assert r1["valid"]
    r2 = svc.validate({"email": "invalid"}, [{"field": "email", "rule": "pattern", "value": r".+@.+\..+"}])
    assert not r2["valid"]


def test_enum():
    svc = SandboxInputValidatorService()
    r = svc.validate({"color": "purple"}, [{"field": "color", "rule": "enum", "value": ["red", "green", "blue"]}])
    assert not r["valid"]


def test_string_length():
    svc = SandboxInputValidatorService()
    r = svc.validate({"bio": "Hi"}, [{"field": "bio", "rule": "minlen", "value": 10}])
    assert not r["valid"]


def test_sanitize_xss():
    svc = SandboxInputValidatorService()
    data = {"name": '<script>alert("xss")</script>', "safe": "hello"}
    sanitized = svc.sanitize(data)
    assert "<script>" not in sanitized["name"]
    assert sanitized["safe"] == "hello"


def test_has_xss():
    svc = SandboxInputValidatorService()
    assert svc.has_xss('<img onerror=alert(1)>') is True
    assert svc.has_xss("hello world") is False


def test_valid_data():
    svc = SandboxInputValidatorService()
    result = svc.validate(
        {"name": "Alice", "age": 30, "role": "admin"},
        [
            {"field": "name", "rule": "required"},
            {"field": "name", "rule": "type", "value": "string"},
            {"field": "age", "rule": "type", "value": "integer"},
            {"field": "role", "rule": "enum", "value": ["admin", "user"]},
        ],
    )
    assert result["valid"]
    assert len(result["errors"]) == 0
