"""Tests for App API Scope — define, assign, check access."""

import pytest

from app.services.app_api_scope import AppAPIScope


class TestDefine:
    def test_define(self):
        s = AppAPIScope()
        scope = s.define_scope("inst-1", "read:users", "Read Users", "Access user data", "users")
        assert scope.category == "users"


class TestAssign:
    def test_assign(self):
        s = AppAPIScope()
        s.define_scope("inst-1", "read:users", "Read Users", "Desc")
        s.define_scope("inst-1", "write:users", "Write Users", "Desc")
        ts = s.assign_scopes("inst-1", "tok-1", ["read:users", "write:users"])
        assert len(ts.scopes) == 2

    def test_undefined_scope(self):
        s = AppAPIScope()
        with pytest.raises(KeyError, match="not defined"):
            s.assign_scopes("inst-1", "tok-1", ["nonexistent"])


class TestCheck:
    def test_all_required(self):
        s = AppAPIScope()
        s.define_scope("inst-1", "read:users", "R", "D")
        s.define_scope("inst-1", "write:users", "W", "D")
        s.assign_scopes("inst-1", "tok-1", ["read:users"])
        assert s.check_access("inst-1", "tok-1", ["read:users"]) is True
        assert s.check_access("inst-1", "tok-1", ["read:users", "write:users"]) is False

    def test_any_mode(self):
        s = AppAPIScope()
        s.define_scope("inst-1", "read:users", "R", "D")
        s.define_scope("inst-1", "write:users", "W", "D")
        s.assign_scopes("inst-1", "tok-1", ["read:users"])
        assert s.check_access("inst-1", "tok-1", ["read:users", "write:users"], mode="any") is True

    def test_no_token(self):
        s = AppAPIScope()
        assert s.check_access("inst-1", "nope", ["read:users"]) is False


class TestIsolation:
    def test_cross(self):
        s = AppAPIScope()
        s.define_scope("inst-1", "read:users", "R", "D")
        assert s.list_scopes("inst-2") == []
