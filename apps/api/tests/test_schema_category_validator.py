"""Schema category validator — exhaustive valid/invalid tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateAppRequest

VALID_CATEGORIES = ["connector", "automation", "analytics", "ui_extension", "ecosystem_source", "content_pack", "workflow_adapter"]
INVALID_CATEGORIES = ["utility", "plugin", "tool", "CONNECTOR", "Automation", "", "random_category"]

@pytest.mark.parametrize("cat", VALID_CATEGORIES)
def test_valid_category(cat):
    r = CreateAppRequest(name="Test", slug="test", category=cat)
    assert r.category == cat

@pytest.mark.parametrize("cat", INVALID_CATEGORIES)
def test_invalid_category(cat):
    with pytest.raises(ValidationError):
        CreateAppRequest(name="Test", slug="test", category=cat)

def test_category_case_sensitive():
    """Categories must be exact lowercase."""
    with pytest.raises(ValidationError):
        CreateAppRequest(name="Test", slug="test", category="Connector")

def test_total_valid_categories():
    assert len(VALID_CATEGORIES) == 7
