"""Parametrized tests for every app category."""

import pytest
from app.services.manifest_validator import VALID_CATEGORIES, validate_manifest
from app.models.developer import AppCategory

ALL_CATS = sorted(VALID_CATEGORIES)

@pytest.mark.parametrize("cat", ALL_CATS)
def test_category_in_manifest(cat):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "category": cat}})
    cat_errors = [e for e in r.errors if "category" in e]
    assert cat_errors == []

@pytest.mark.parametrize("cat", ALL_CATS)
def test_category_lowercase(cat):
    assert cat == cat.lower()

@pytest.mark.parametrize("cat", ALL_CATS)
def test_category_in_enum(cat):
    assert cat in [c.value for c in AppCategory]

def test_category_count():
    assert len(VALID_CATEGORIES) == 7
    assert len(AppCategory) == 7
