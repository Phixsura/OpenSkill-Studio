"""Manifest invalid category validation."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_CATEGORIES

BASE = {"schema_version": "1.0", "permissions": ["read:cohorts"]}

INVALID_CATS = ["plugin", "tool", "widget", "service", "middleware", "CONNECTOR"]

@pytest.mark.parametrize("cat", INVALID_CATS)
def test_invalid_category_rejected(cat):
    m = {**BASE, "app": {"name": "X", "slug": "cat-test", "version": "1.0.0", "category": cat}}
    r = validate_manifest(m)
    assert not r.valid or any("category" in e.lower() for e in r.errors)

@pytest.mark.parametrize("cat", sorted(VALID_CATEGORIES))
def test_valid_category_accepted(cat):
    m = {**BASE, "app": {"name": "X", "slug": "cat-test", "version": "1.0.0", "category": cat}}
    r = validate_manifest(m)
    cat_errors = [e for e in r.errors if "category" in e.lower()]
    assert cat_errors == []

def test_valid_categories_count():
    assert len(VALID_CATEGORIES) >= 7
