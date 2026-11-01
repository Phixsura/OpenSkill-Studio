"""Tests for App API Webhook Payload Schema — define, validate."""

import pytest
from app.services.app_api_webhook_payload_schema import AppAPIWebhookPayloadSchema


class TestDefine:
    def test_define(self):
        s = AppAPIWebhookPayloadSchema()
        schema = s.define("inst-1", "push", ["repo", "ref"], ["sender"])
        assert len(schema.required_fields) == 2


class TestValidate:
    def test_valid(self):
        s = AppAPIWebhookPayloadSchema()
        s.define("inst-1", "push", ["repo", "ref"], ["sender"])
        errors = s.validate("inst-1", "push", {"repo": "x", "ref": "main"})
        assert errors == []

    def test_missing_required(self):
        s = AppAPIWebhookPayloadSchema()
        s.define("inst-1", "push", ["repo", "ref"])
        errors = s.validate("inst-1", "push", {"repo": "x"})
        assert len(errors) == 1

    def test_unknown_field(self):
        s = AppAPIWebhookPayloadSchema()
        s.define("inst-1", "push", ["repo"], [])
        errors = s.validate("inst-1", "push", {"repo": "x", "extra": "y"})
        assert any("Unknown" in e for e in errors)

    def test_pass_rate(self):
        s = AppAPIWebhookPayloadSchema()
        s.define("inst-1", "push", ["repo"])
        s.validate("inst-1", "push", {"repo": "x"})
        s.validate("inst-1", "push", {})  # fail
        schema = s.list_schemas("inst-1")[0]
        assert schema.pass_rate == 50.0


class TestIsolation:
    def test_cross(self):
        s = AppAPIWebhookPayloadSchema()
        s.define("inst-1", "push", ["repo"])
        assert s.list_schemas("inst-2") == []
