"""OAuth scope validator tests."""

import pytest
from app.services.app_scope_validator import validate_scopes, parse_scope_string, format_scope_string

def test_valid_scopes():
    result = validate_scopes(["read:cohorts", "write:projects"], ["read:cohorts", "write:projects", "read:skills"])
    assert result["valid"] is True
    assert result["granted"] == ["read:cohorts", "write:projects"]
    assert result["denied"] == []

def test_scope_not_in_manifest():
    result = validate_scopes(["read:cohorts", "write:cohorts"], ["read:cohorts"])
    assert result["valid"] is False
    assert "write:cohorts" in result["denied"]

def test_unknown_scope():
    result = validate_scopes(["admin:everything"], ["read:cohorts"])
    assert result["valid"] is False
    assert "admin:everything" in result["denied"]

def test_empty_scopes():
    result = validate_scopes([], ["read:cohorts"])
    assert result["valid"] is True
    assert result["granted"] == []

def test_parse_scope_string():
    assert parse_scope_string("read:cohorts write:projects") == ["read:cohorts", "write:projects"]

def test_parse_scope_string_extra_spaces():
    assert parse_scope_string("  read:cohorts   write:projects  ") == ["read:cohorts", "write:projects"]

def test_parse_empty():
    assert parse_scope_string("") == []

def test_format_scope_string():
    result = format_scope_string(["write:projects", "read:cohorts"])
    assert result == "read:cohorts write:projects"  # sorted

def test_format_empty():
    assert format_scope_string([]) == ""
