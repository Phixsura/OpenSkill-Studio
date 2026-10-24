from app.services.app_marketplace_app_app_form_validator import validate_field, validate_form

def test_required():
    r = validate_field(value="", rules=[{"type": "required"}])
    assert not r["valid"]

def test_email():
    assert validate_field(value="a@b.com", rules=[{"type": "email"}])["valid"]
    assert not validate_field(value="bad", rules=[{"type": "email"}])["valid"]

def test_min_max():
    assert not validate_field(value="ab", rules=[{"type": "min_length", "min": 3}])["valid"]
    assert not validate_field(value="abcdef", rules=[{"type": "max_length", "max": 3}])["valid"]

def test_form():
    schema = {"name": [{"type": "required"}, {"type": "min_length", "min": 2}],
              "email": [{"type": "required"}, {"type": "email"}]}
    r = validate_form(fields={"name": "A", "email": "bad"}, schema=schema)
    assert not r["valid"]
    assert r["error_count"] == 2
