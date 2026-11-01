"""Tests for App API Key Scope — create, validate, revoke."""

import pytest

from app.services.app_api_key_scope import AppAPIKeyScope


class TestCreate:
    def test_create(self):
        s = AppAPIKeyScope()
        key, raw = s.create_key("inst-1", "k1", ["read:data", "write:data"], "Prod Key")
        assert key.scopes == {"read:data", "write:data"}
        assert len(raw) > 20

    def test_no_scopes(self):
        s = AppAPIKeyScope()
        with pytest.raises(ValueError):
            s.create_key("inst-1", "k1", [])


class TestValidate:
    def test_valid_scope(self):
        s = AppAPIKeyScope()
        _, raw = s.create_key("inst-1", "k1", ["read:data"])
        assert s.validate("inst-1", raw, "read:data") is True

    def test_missing_scope(self):
        s = AppAPIKeyScope()
        _, raw = s.create_key("inst-1", "k1", ["read:data"])
        assert s.validate("inst-1", raw, "write:data") is False

    def test_revoked(self):
        s = AppAPIKeyScope()
        _, raw = s.create_key("inst-1", "k1", ["read:data"])
        s.revoke("inst-1", "k1")
        assert s.validate("inst-1", raw, "read:data") is False


class TestList:
    def test_by_scope(self):
        s = AppAPIKeyScope()
        s.create_key("inst-1", "k1", ["read:data"])
        s.create_key("inst-1", "k2", ["write:data"])
        assert len(s.list_keys("inst-1", scope="read:data")) == 1


class TestIsolation:
    def test_cross(self):
        s = AppAPIKeyScope()
        s.create_key("inst-1", "k1", ["read:data"])
        assert s.list_keys("inst-2") == []
