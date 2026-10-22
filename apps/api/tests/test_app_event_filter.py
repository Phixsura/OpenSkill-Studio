"""Event filter builder tests."""

import pytest
from app.services.app_event_filter import build_filter, validate_filter, combine_filters, matches, VALID_OPERATORS

@pytest.mark.parametrize("op", sorted(VALID_OPERATORS))
def test_build_valid_operator(op):
    f = build_filter("status", op, "active")
    assert f["operator"] == op

def test_build_invalid_operator():
    with pytest.raises(ValueError):
        build_filter("x", "INVALID", "y")

def test_build_empty_field():
    with pytest.raises(ValueError):
        build_filter("", "eq", "y")

def test_validate_valid():
    assert validate_filter({"field": "x", "operator": "eq", "value": 1}) == []

def test_validate_missing_field():
    errors = validate_filter({"operator": "eq", "value": 1})
    assert any("field" in e for e in errors)

def test_validate_invalid_operator():
    errors = validate_filter({"field": "x", "operator": "bad", "value": 1})
    assert any("operator" in e.lower() for e in errors)

def test_combine():
    f1 = build_filter("a", "eq", 1)
    f2 = build_filter("b", "gte", 10)
    result = combine_filters(f1, f2)
    assert len(result) == 2

def test_matches_eq():
    assert matches({"status": "active"}, {"field": "status", "operator": "eq", "value": "active"})

def test_matches_neq():
    assert matches({"status": "active"}, {"field": "status", "operator": "neq", "value": "inactive"})

def test_matches_nested():
    assert matches({"user": {"role": "admin"}}, {"field": "user.role", "operator": "eq", "value": "admin"})

def test_matches_gte():
    assert matches({"score": 95}, {"field": "score", "operator": "gte", "value": 90})

def test_matches_contains():
    assert matches({"name": "hello world"}, {"field": "name", "operator": "contains", "value": "world"})
