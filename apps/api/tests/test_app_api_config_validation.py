"""Tests for App API Config Validation — rules, validate."""

import pytest
from app.services.app_api_config_validation import AppAPIConfigValidation


class TestAdd:
    def test_add(self):
        v = AppAPIConfigValidation()
        r = v.add_rule("inst-1", "db_host", "required")
        assert r.rule_type == "required"


class TestValidate:
    def test_required_missing(self):
        v = AppAPIConfigValidation()
        v.add_rule("inst-1", "db_host", "required")
        errors = v.validate("inst-1", {})
        assert len(errors) == 1

    def test_enum(self):
        v = AppAPIConfigValidation()
        v.add_rule("inst-1", "env", "enum", "prod,staging,dev")
        assert v.validate("inst-1", {"env": "prod"}) == []
        assert len(v.validate("inst-1", {"env": "test"})) == 1

    def test_min_max(self):
        v = AppAPIConfigValidation()
        v.add_rule("inst-1", "port", "min", "1024")
        v.add_rule("inst-1", "port", "max", "65535")
        assert v.validate("inst-1", {"port": "8080"}) == []
        assert len(v.validate("inst-1", {"port": "80"})) == 1

    def test_valid_config(self):
        v = AppAPIConfigValidation()
        v.add_rule("inst-1", "host", "required")
        assert v.validate("inst-1", {"host": "localhost"}) == []


class TestIsolation:
    def test_cross(self):
        v = AppAPIConfigValidation()
        v.add_rule("inst-1", "key", "required")
        assert v.validate("inst-2", {}) == []
