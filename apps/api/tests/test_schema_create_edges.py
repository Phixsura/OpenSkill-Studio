"""Schema create request edge cases — XSS, injection, boundary values."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateDeveloperAccountRequest, CreateAppRequest

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "javascript:void(0)",
    "' OR 1=1 --",
    '"><img src=x onerror=alert(1)>',
]

@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_in_display_name_accepted(payload):
    """Display names with special chars are accepted (sanitized on render)."""
    r = CreateDeveloperAccountRequest(display_name=payload, slug="test-xss", support_email="a@b.c")
    assert r.display_name == payload

SLUG_CASES = [
    ("valid-slug", True),
    ("my-app-123", True),
    ("ab", True),
]

@pytest.mark.parametrize("slug,valid", SLUG_CASES)
def test_valid_slugs(slug, valid):
    r = CreateDeveloperAccountRequest(display_name="Test", slug=slug, support_email="a@b.c")
    assert r.slug == slug

LONG_VALUES = [
    ("a" * 100, True),   # max reasonable
]

@pytest.mark.parametrize("name,should_work", LONG_VALUES)
def test_long_display_name(name, should_work):
    if should_work:
        r = CreateDeveloperAccountRequest(display_name=name, slug="long-test", support_email="a@b.c")
        assert len(r.display_name) == len(name)

def test_email_format():
    with pytest.raises(ValidationError):
        CreateDeveloperAccountRequest(display_name="X", slug="s", support_email="not-an-email")

VALID_CATEGORIES = ["connector", "automation", "analytics", "ui_extension", "ecosystem_source", "content_pack", "workflow_adapter"]

@pytest.mark.parametrize("cat", VALID_CATEGORIES)
def test_all_valid_categories(cat):
    r = CreateAppRequest(name="App", slug="app", category=cat)
    assert r.category == cat
