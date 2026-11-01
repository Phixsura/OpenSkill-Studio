"""Tests for App Webhook Payload Validator — fields, types, nesting, size."""

import pytest

from app.services.app_webhook_payload_validator import (
    AppWebhookPayloadValidator,
    FieldSpec,
    MAX_PAYLOAD_BYTES,
    ValidationSeverity,
)

SCHEMA = [
    FieldSpec("event_id", "string"),
    FieldSpec("event_type", "string"),
    FieldSpec("score", "number"),
    FieldSpec("passed", "boolean"),
    FieldSpec("tags", "array", required=False),
    FieldSpec("metadata", "object", required=False, children={
        "source": FieldSpec("source", "string"),
        "version": FieldSpec("version", "string", required=False),
    }),
]


class TestBasicValidation:
    def test_valid_payload(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True},
            SCHEMA,
        )
        assert result.valid is True
        assert result.error_count == 0

    def test_missing_required_field(self):
        v = AppWebhookPayloadValidator()
        result = v.validate({"event_type": "test", "score": 95, "passed": True}, SCHEMA)
        assert result.valid is False
        assert any("event_id" in i.field_path for i in result.issues)

    def test_optional_field_missing_ok(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True},
            SCHEMA,
        )
        assert result.valid is True  # tags is optional


class TestTypeChecking:
    def test_wrong_type_string(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": 123, "event_type": "test", "score": 95, "passed": True},
            SCHEMA,
        )
        assert result.valid is False
        assert any("string" in i.message for i in result.issues)

    def test_wrong_type_number(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": "high", "passed": True},
            SCHEMA,
        )
        assert result.valid is False

    def test_wrong_type_boolean(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": "yes"},
            SCHEMA,
        )
        assert result.valid is False

    def test_boolean_not_number(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": True, "passed": True},
            SCHEMA,
        )
        assert result.valid is False  # True is bool, not number

    def test_array_type(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True, "tags": ["a", "b"]},
            SCHEMA,
        )
        assert result.valid is True

    def test_wrong_type_array(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True, "tags": "not-array"},
            SCHEMA,
        )
        assert result.valid is False


class TestNestedObjects:
    def test_valid_nested(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True,
             "metadata": {"source": "api"}},
            SCHEMA,
        )
        assert result.valid is True

    def test_nested_missing_required(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True,
             "metadata": {"version": "2.0"}},  # missing source
            SCHEMA,
        )
        assert result.valid is False
        assert any("source" in i.field_path for i in result.issues)

    def test_nested_wrong_type(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True,
             "metadata": {"source": 123}},
            SCHEMA,
        )
        assert result.valid is False


class TestSizeLimit:
    def test_oversized_payload(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True,
             "big_field": "x" * (MAX_PAYLOAD_BYTES + 1)},
            SCHEMA,
        )
        assert any("size" in i.message.lower() for i in result.issues)

    def test_normal_size_ok(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True},
            SCHEMA,
        )
        assert not any("size" in i.message.lower() for i in result.issues)


class TestExtraFields:
    def test_undeclared_field_warning(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True,
             "extra_stuff": "hello"},
            SCHEMA,
        )
        assert result.valid is True  # warnings don't fail
        assert result.warning_count >= 1
        assert any("Undeclared" in i.message for i in result.issues)


class TestResultCounts:
    def test_fields_checked(self):
        v = AppWebhookPayloadValidator()
        result = v.validate(
            {"event_id": "e1", "event_type": "test", "score": 95, "passed": True},
            SCHEMA,
        )
        assert result.fields_checked >= 4

    def test_payload_bytes(self):
        v = AppWebhookPayloadValidator()
        result = v.validate({"event_id": "e1", "event_type": "t", "score": 1, "passed": True}, SCHEMA)
        assert result.payload_bytes > 0
