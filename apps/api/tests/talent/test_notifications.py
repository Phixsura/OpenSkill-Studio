"""Notification system tests — models, service logic, schema validation."""

from app.talent.models.notification import (
    NOTIFICATION_EVENT_TYPES,
    NotificationPreference,
    TalentNotification,
)
from app.talent.schemas.notification import (
    NotificationPreferenceResponse,
    NotificationResponse,
    UnreadCountResponse,
    UpdatePreferencesRequest,
)


class TestNotificationEventTypes:
    def test_has_application_events(self):
        assert "application_status_changed" in NOTIFICATION_EVENT_TYPES

    def test_has_match_events(self):
        assert "new_match_found" in NOTIFICATION_EVENT_TYPES

    def test_has_credential_events(self):
        assert "credential_issued" in NOTIFICATION_EVENT_TYPES

    def test_has_endorsement_events(self):
        assert "endorsement_received" in NOTIFICATION_EVENT_TYPES

    def test_has_outreach_events(self):
        assert "outreach_received" in NOTIFICATION_EVENT_TYPES

    def test_has_interview_events(self):
        assert "interview_scheduled" in NOTIFICATION_EVENT_TYPES

    def test_has_offer_events(self):
        assert "offer_extended" in NOTIFICATION_EVENT_TYPES

    def test_has_pool_events(self):
        assert "pool_invitation" in NOTIFICATION_EVENT_TYPES

    def test_has_passport_events(self):
        assert "passport_viewed" in NOTIFICATION_EVENT_TYPES

    def test_count(self):
        assert len(NOTIFICATION_EVENT_TYPES) == 9


class TestNotificationModels:
    def test_preference_tablename(self):
        assert NotificationPreference.__tablename__ == "talent_notification_preferences"

    def test_notification_tablename(self):
        assert TalentNotification.__tablename__ == "talent_notifications"


class TestNotificationSchemas:
    def test_response_schema(self):
        resp = NotificationResponse(
            id="test",
            user_id="user1",
            event_type="credential_issued",
            title="Credential Issued",
            message="You earned a new credential",
            extra={"credential_id": "c1"},
        )
        assert resp.id == "test"
        assert resp.extra == {"credential_id": "c1"}

    def test_preference_response(self):
        pref = NotificationPreferenceResponse(
            event_type="application_status_changed",
            channel="in_app",
            enabled=True,
        )
        assert pref.enabled is True

    def test_unread_count(self):
        count = UnreadCountResponse(count=5)
        assert count.count == 5

    def test_update_preferences_request(self):
        req = UpdatePreferencesRequest(
            preferences=[
                {"event_type": "credential_issued", "enabled": False},
                {"event_type": "new_match_found", "enabled": True},
            ]
        )
        assert len(req.preferences) == 2

    def test_update_preferences_min_length(self):
        import pytest

        with pytest.raises(ValueError):
            UpdatePreferencesRequest(preferences=[])
