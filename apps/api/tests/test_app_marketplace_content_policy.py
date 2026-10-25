from app.services.app_marketplace_content_policy import ContentPolicy


def test_valid_metadata():
    cp = ContentPolicy()
    ok, violations = cp.validate({
        "name": "My Cool Extension",
        "description": "A really useful extension that helps developers be more productive.",
        "category": "tools",
        "version": "1.0.0",
    })
    assert ok is True
    assert len(violations) == 0


def test_reserved_name():
    cp = ContentPolicy()
    violations = cp.validate_name("OpenSkill")
    assert any(v.rule == "reserved" for v in violations)


def test_name_too_long():
    cp = ContentPolicy()
    violations = cp.validate_name("x" * 100)
    assert any(v.rule == "max_length" for v in violations)


def test_description_too_short():
    cp = ContentPolicy()
    violations = cp.validate_description("Short")
    assert any(v.rule == "min_length" for v in violations)


def test_forbidden_content():
    cp = ContentPolicy()
    violations = cp.validate_description("This extension helps you get rich quick with free money schemes")
    assert any(v.rule == "forbidden_content" for v in violations)


def test_invalid_category():
    cp = ContentPolicy()
    violations = cp.validate_category("invalid_cat")
    assert len(violations) == 1


def test_invalid_version():
    cp = ContentPolicy()
    violations = cp.validate_version("not.a.version.lol")
    assert len(violations) == 1
    assert cp.validate_version("1.2.3-beta.1") == []


def test_full_validation_fails():
    cp = ContentPolicy()
    ok, violations = cp.validate({"name": "", "description": "too short", "version": "bad"})
    assert ok is False
    assert len(violations) >= 3
