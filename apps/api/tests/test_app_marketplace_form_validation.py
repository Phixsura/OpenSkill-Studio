from app.services.app_marketplace_form_validation import validate_field, validate_form

def test_required_ok():
    r = validate_field(value="hello", rules=["required"])
    assert r["valid"]

def test_required_fail():
    r = validate_field(value="", rules=["required"])
    assert not r["valid"]

def test_email():
    assert validate_field(value="a@b.com", rules=["email"])["valid"]
    assert not validate_field(value="invalid", rules=["email"])["valid"]

def test_url():
    assert validate_field(value="https://x.com", rules=["url"])["valid"]
    assert not validate_field(value="not-url", rules=["url"])["valid"]

def test_slug():
    assert validate_field(value="my-app", rules=["slug"])["valid"]
    assert not validate_field(value="My App!", rules=["slug"])["valid"]

def test_form():
    schema = {"name": ["required", "min_length_3"], "email": ["required", "email"]}
    r = validate_form(fields={"name": "App", "email": "a@b.com"}, schema=schema)
    assert r["valid"]

def test_form_errors():
    schema = {"name": ["required"], "email": ["email"]}
    r = validate_form(fields={"name": "", "email": "bad"}, schema=schema)
    assert not r["valid"]
    assert r["error_count"] == 2
