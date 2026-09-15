"""Tests for gaps #146-155: Communication Intelligence."""

from app.talent.services.communication_intelligence import (
    DIGEST_FREQUENCIES,
    MAX_BULK_RECIPIENTS,
    build_digest,
    list_email_templates,
    list_message_templates,
    render_email_template,
    render_message_template,
    validate_bulk_message,
)


class TestEmailTemplates:
    def test_list(self):
        templates = list_email_templates()
        assert "application_status_changed" in templates
        assert "credential_issued" in templates
        assert len(templates) >= 7

    def test_render(self):
        result = render_email_template("credential_issued", {
            "candidate_name": "Alice",
            "credential_type": "AI Visual — Foundation",
            "credential_url": "https://example.com/cred/1",
        })
        assert result is not None
        assert "Alice" in result["body"]
        assert "AI Visual" in result["body"]

    def test_render_unknown(self):
        assert render_email_template("nonexistent", {}) is None

    def test_render_missing_vars(self):
        result = render_email_template("credential_issued", {})
        assert result is not None  # falls back to raw template


class TestDigest:
    def test_empty(self):
        digest = build_digest([], "daily")
        assert digest["count"] == 0

    def test_with_notifications(self):
        notifs = [
            {"event_type": "application_status_changed", "title": "Status updated"},
            {"event_type": "application_status_changed", "title": "Another update"},
            {"event_type": "credential_issued", "title": "New credential"},
        ]
        digest = build_digest(notifs, "weekly")
        assert digest["count"] == 3
        assert len(digest["sections"]) == 2

    def test_frequencies(self):
        assert "daily" in DIGEST_FREQUENCIES
        assert "weekly" in DIGEST_FREQUENCIES
        assert "none" in DIGEST_FREQUENCIES


class TestMessageTemplates:
    def test_list(self):
        templates = list_message_templates()
        assert "thank_you" in templates
        assert "rejection_kind" in templates
        assert len(templates) >= 5

    def test_render(self):
        result = render_message_template("next_steps", {"stage_type": "technical"})
        assert result is not None
        assert "technical" in result

    def test_render_unknown(self):
        assert render_message_template("nonexistent", {}) is None


class TestBulkMessaging:
    def test_valid(self):
        errors = validate_bulk_message(["u1", "u2"], "Hello everyone!")
        assert errors == []

    def test_empty_recipients(self):
        errors = validate_bulk_message([], "Hello")
        assert any("recipient" in e.lower() for e in errors)

    def test_too_many(self):
        ids = [f"u{i}" for i in range(150)]
        errors = validate_bulk_message(ids, "Hello")
        assert any(str(MAX_BULK_RECIPIENTS) in e for e in errors)

    def test_duplicates(self):
        errors = validate_bulk_message(["u1", "u1"], "Hello")
        assert any("duplicate" in e.lower() for e in errors)

    def test_short_content(self):
        errors = validate_bulk_message(["u1"], "Hi")
        assert any("5" in e for e in errors)

    def test_long_content(self):
        errors = validate_bulk_message(["u1"], "x" * 6000)
        assert any("5000" in e for e in errors)
