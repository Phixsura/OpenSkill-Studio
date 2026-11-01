"""Tests for App Request Validator — rules, validation, errors."""

import pytest

from app.services.app_request_validator import AppRequestValidator


class TestAddRule:
    def test_add(self):
        v = AppRequestValidator()
        r = v.add_rule("inst-1", "r1", "required_header", "Authorization")
        assert r.rule_type == "required_header"

    def test_unknown_type(self):
        v = AppRequestValidator()
        with pytest.raises(ValueError, match="Unknown"):
            v.add_rule("inst-1", "r1", "bogus", "x")


class TestValidate:
    def test_header_present(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "required_header", "Authorization")
        result = v.validate("inst-1", {"Authorization": "Bearer xyz"})
        assert result.valid is True

    def test_header_missing(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "required_header", "Authorization")
        result = v.validate("inst-1", {})
        assert result.valid is False
        assert result.errors[0].code == "missing_header"

    def test_content_type(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "content_type", "application/json")
        result = v.validate("inst-1", {}, content_type="text/plain")
        assert result.valid is False
        assert result.errors[0].code == "invalid_content_type"

    def test_max_size(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "max_size", "1024")
        result = v.validate("inst-1", {}, body_size=2000)
        assert result.valid is False
        assert result.errors[0].code == "body_too_large"

    def test_disabled_rule(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "required_header", "X-Custom")
        v.toggle("inst-1", "r1", False)
        result = v.validate("inst-1", {})
        assert result.valid is True


class TestIsolation:
    def test_cross(self):
        v = AppRequestValidator()
        v.add_rule("inst-1", "r1", "required_header", "X-Custom")
        result = v.validate("inst-2", {})
        assert result.valid is True
