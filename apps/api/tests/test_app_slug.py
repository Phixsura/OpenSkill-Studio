"""App slug utility tests."""

import pytest
from app.services.app_slug import validate_slug, generate_slug, is_slug_available, RESERVED_SLUGS

VALID_SLUGS = ["my-app", "test-connector", "ab", "a123", "cool-app-v2"]

@pytest.mark.parametrize("slug", VALID_SLUGS)
def test_valid(slug):
    assert validate_slug(slug) == []

INVALID_SLUGS = [
    ("", "empty"),
    ("a", "too short"),
    ("A-Upper", "uppercase"),
    ("has space", "spaces"),
    ("-start-dash", "starts with dash"),
    ("a" * 61, "too long"),
    ("has--double", "consecutive hyphens"),
]

@pytest.mark.parametrize("slug,reason", INVALID_SLUGS, ids=lambda x: str(x)[:20])
def test_invalid(slug, reason):
    errors = validate_slug(slug)
    assert len(errors) > 0, f"{slug} should be invalid ({reason})"

@pytest.mark.parametrize("reserved", sorted(list(RESERVED_SLUGS))[:5])
def test_reserved_rejected(reserved):
    errors = validate_slug(reserved)
    assert any("reserved" in e for e in errors)

GENERATE_CASES = [
    ("My Cool App", "my-cool-app"),
    ("LMS Connector v2", "lms-connector-v2"),
    ("  Spaces  ", "spaces"),
    ("Under_Score", "underscore"),
]

@pytest.mark.parametrize("name,expected", GENERATE_CASES)
def test_generate(name, expected):
    assert generate_slug(name) == expected

def test_generate_truncates():
    slug = generate_slug("a" * 100)
    assert len(slug) <= 60

def test_availability_taken():
    assert is_slug_available("my-app", {"my-app", "other"}) is False

def test_availability_free():
    assert is_slug_available("new-app", {"my-app"}) is True

def test_availability_reserved():
    assert is_slug_available("admin", set()) is False
