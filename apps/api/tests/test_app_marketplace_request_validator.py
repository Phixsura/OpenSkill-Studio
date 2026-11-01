from app.services.app_marketplace_request_validator import RequestValidator


def test_required_fields():
    rv = RequestValidator()
    ok, errors = rv.validate({"name": "test"}, required=["name", "email"])
    assert ok is False
    assert any(e.field == "email" for e in errors)


def test_type_validation():
    rv = RequestValidator()
    ok, errors = rv.validate({"age": "thirty"}, types={"age": "int"})
    assert ok is False
    assert errors[0].code == "type_error"


def test_length_validation():
    rv = RequestValidator()
    ok, errors = rv.validate({"name": "x" * 200}, lengths={"name": 100})
    assert ok is False
    assert errors[0].code == "max_length"


def test_pattern_validation():
    rv = RequestValidator()
    ok, _ = rv.validate({"email": "bad"}, patterns={"email": r"^[^@]+@[^@]+\.[^@]+$"})
    assert ok is False
    ok2, _ = rv.validate({"email": "a@b.com"}, patterns={"email": r"^[^@]+@[^@]+\.[^@]+$"})
    assert ok2 is True


def test_sanitize_xss():
    rv = RequestValidator()
    assert "<script>" not in rv.sanitize_string('hello<script>alert("xss")</script>world')
    assert "javascript:" not in rv.sanitize_string('javascript:alert(1)')


def test_sanitize_dict():
    rv = RequestValidator()
    data = {"name": "ok", "bio": '<script>bad</script>Safe text', "nested": {"x": "javascript:void"}}
    clean = rv.sanitize_dict(data)
    assert "<script>" not in clean["bio"]
    assert "javascript:" not in clean["nested"]["x"]


def test_all_valid():
    rv = RequestValidator()
    ok, errors = rv.validate(
        {"name": "Alice", "age": 30, "email": "a@b.com"},
        required=["name", "email"],
        types={"name": "string", "age": "int"},
        lengths={"name": 100},
        patterns={"email": r"^[^@]+@[^@]+\.[^@]+$"},
    )
    assert ok is True
    assert len(errors) == 0
