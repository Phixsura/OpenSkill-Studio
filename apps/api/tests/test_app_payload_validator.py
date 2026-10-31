"""Tests for App Payload Validator — schemas, validation, success rate."""

import pytest

from app.services.app_payload_validator import AppPayloadValidator


class TestRegister:
    def test_register(self):
        v = AppPayloadValidator()
        s = v.register_schema("inst-1", "user.created", ["id", "email"], ["name"])
        assert s.required_fields == ["id", "email"]

    def test_missing_event_type(self):
        v = AppPayloadValidator()
        with pytest.raises(ValueError):
            v.register_schema("inst-1", "", ["id"])


class TestValidate:
    def test_valid(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "user.created", ["id", "email"])
        r = v.validate("inst-1", "user.created", {"id": "u1", "email": "a@b.com"})
        assert r.valid is True
        assert r.missing_fields == []

    def test_missing_required(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "user.created", ["id", "email"])
        r = v.validate("inst-1", "user.created", {"id": "u1"})
        assert r.valid is False
        assert "email" in r.missing_fields

    def test_unknown_fields(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "user.created", ["id"], ["name"])
        r = v.validate("inst-1", "user.created", {"id": "u1", "extra": "val"})
        assert "extra" in r.unknown_fields

    def test_optional_ok(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "user.created", ["id"], ["name"])
        r = v.validate("inst-1", "user.created", {"id": "u1", "name": "Alice"})
        assert r.valid is True
        assert r.unknown_fields == []

    def test_unknown_event_type(self):
        v = AppPayloadValidator()
        with pytest.raises(KeyError):
            v.validate("inst-1", "nope", {})


class TestSuccessRate:
    def test_rate(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "e", ["id"])
        v.validate("inst-1", "e", {"id": "1"})  # pass
        v.validate("inst-1", "e", {})  # fail
        assert v.success_rate("inst-1", "e") == 50.0

    def test_no_checks(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "e", ["id"])
        assert v.success_rate("inst-1", "e") == 100.0


class TestIsolation:
    def test_cross_installation(self):
        v = AppPayloadValidator()
        v.register_schema("inst-1", "e", ["id"])
        with pytest.raises(KeyError):
            v.validate("inst-2", "e", {})
