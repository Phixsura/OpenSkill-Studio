from app.services.app_marketplace_app_data_validator import validate, validate_batch

def test_email_valid():
    assert validate(value="alice@example.com", format_type="email")["valid"]

def test_email_invalid():
    assert not validate(value="not-email", format_type="email")["valid"]

def test_semver():
    assert validate(value="1.2.3", format_type="semver")["valid"]
    assert validate(value="1.0.0-beta.1", format_type="semver")["valid"]
    assert not validate(value="v1.2", format_type="semver")["valid"]

def test_slug():
    assert validate(value="my-cool-app", format_type="slug")["valid"]
    assert not validate(value="Bad Slug!", format_type="slug")["valid"]

def test_batch():
    items = [
        {"field": "email", "value": "a@b.com", "format": "email"},
        {"field": "version", "value": "nope", "format": "semver"},
    ]
    r = validate_batch(items=items)
    assert r["valid_count"] == 1
    assert not r["all_valid"]
