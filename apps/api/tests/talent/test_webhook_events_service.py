"""Webhook events service tests."""

from app.talent.services.webhook_events import TALENT_EVENT_TYPES


class TestWebhookEventTypes:
    def test_has_core_events(self):
        assert "credential.issued" in TALENT_EVENT_TYPES
        assert "application.submitted" in TALENT_EVENT_TYPES
        assert "application.stage_changed" in TALENT_EVENT_TYPES
        assert "offer.created" in TALENT_EVENT_TYPES
        assert "placement.started" in TALENT_EVENT_TYPES
        assert "placement.completed" in TALENT_EVENT_TYPES
        assert "capability.verified" in TALENT_EVENT_TYPES

    def test_has_employer_events(self):
        assert "employer_verification.submitted" in TALENT_EVENT_TYPES

    def test_has_outreach_events(self):
        assert "outreach.sent" in TALENT_EVENT_TYPES
        assert "outreach.responded" in TALENT_EVENT_TYPES

    def test_has_pool_events(self):
        assert "talent_pool.member_added" in TALENT_EVENT_TYPES

    def test_has_credential_revoked(self):
        assert "credential.revoked" in TALENT_EVENT_TYPES

    def test_minimum_event_count(self):
        assert len(TALENT_EVENT_TYPES) >= 12
