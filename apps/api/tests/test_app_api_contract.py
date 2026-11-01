"""Tests for App API Contract — define, validate, violations."""

import pytest

from app.services.app_api_contract import AppAPIContract

REQ_FIELDS = [{"name": "title", "type": "string"}, {"name": "count", "type": "int", "required": False}]
RESP_FIELDS = [{"name": "id", "type": "string"}, {"name": "created", "type": "bool"}]


class TestDefine:
    def test_define(self):
        c = AppAPIContract()
        ct = c.define("inst-1", "c1", "POST", "/api/items", REQ_FIELDS, RESP_FIELDS)
        assert len(ct.request_fields) == 2


class TestValidate:
    def test_valid(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api/items", REQ_FIELDS)
        errors = c.validate_payload("inst-1", "c1", {"title": "Hello"})
        assert errors == []

    def test_missing_required(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api/items", REQ_FIELDS)
        errors = c.validate_payload("inst-1", "c1", {})
        assert any("title" in e for e in errors)

    def test_wrong_type(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api/items", REQ_FIELDS)
        errors = c.validate_payload("inst-1", "c1", {"title": 123})
        assert any("string" in e for e in errors)

    def test_bool_guard(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api", [{"name": "n", "type": "int"}])
        errors = c.validate_payload("inst-1", "c1", {"n": True})
        assert any("bool" in e for e in errors)

    def test_optional_missing_ok(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api/items", REQ_FIELDS)
        errors = c.validate_payload("inst-1", "c1", {"title": "X"})
        assert errors == []


class TestIsolation:
    def test_cross(self):
        c = AppAPIContract()
        c.define("inst-1", "c1", "POST", "/api")
        assert c.list_contracts("inst-2") == []
