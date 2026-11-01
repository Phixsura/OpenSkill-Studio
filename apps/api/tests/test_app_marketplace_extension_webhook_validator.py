from app.services.app_marketplace_extension_webhook_validator import (
    WebhookValidatorService,
)
import json


def test_valid_payload():
    svc = WebhookValidatorService()
    svc.register_schema("push", required_fields=["ref", "commits"],
                        field_types={"ref": "string", "commits": "array"})
    result = svc.validate("push", json.dumps({"ref": "main", "commits": []}))
    assert result.valid is True
    assert result.parsed_payload is not None


def test_missing_required():
    svc = WebhookValidatorService()
    svc.register_schema("push", required_fields=["ref", "commits"])
    result = svc.validate("push", json.dumps({"ref": "main"}))
    assert result.valid is False
    assert any("commits" in e for e in result.errors)


def test_wrong_type():
    svc = WebhookValidatorService()
    svc.register_schema("deploy", field_types={"count": "integer"})
    result = svc.validate("deploy", json.dumps({"count": "five"}))
    assert result.valid is False
    assert any("expected integer" in e for e in result.errors)


def test_unknown_event():
    svc = WebhookValidatorService()
    result = svc.validate("unknown", "{}")
    assert result.valid is False


def test_invalid_json():
    svc = WebhookValidatorService()
    svc.register_schema("push")
    result = svc.validate("push", "not json")
    assert result.valid is False
    assert any("Invalid JSON" in e for e in result.errors)


def test_payload_too_large():
    svc = WebhookValidatorService()
    svc.register_schema("push", max_payload_bytes=100)
    result = svc.validate("push", json.dumps({"data": "x" * 200}))
    assert result.valid is False
    assert any("too large" in e for e in result.errors)


def test_required_headers():
    svc = WebhookValidatorService()
    svc.register_schema("push", required_headers=["X-Signature"])
    result = svc.validate("push", json.dumps({"ok": True}), headers={})
    assert result.valid is False
    assert any("X-Signature" in e for e in result.errors)


def test_empty_field_warning():
    svc = WebhookValidatorService()
    svc.register_schema("push", required_fields=["name"])
    result = svc.validate("push", json.dumps({"name": ""}))
    assert result.valid is True
    assert any("empty" in w for w in result.warnings)
