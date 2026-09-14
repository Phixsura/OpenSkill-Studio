"""Data retention and consent audit tests (N20)."""

from app.talent.models.consent_log import (
    CONSENT_ACTIONS,
    CONSENT_TYPES,
)
from app.talent.services.data_retention import (
    RETENTION_POLICIES,
    RetentionReport,
)


class TestRetentionPolicies:
    def test_notification_retention_90_days(self):
        assert RETENTION_POLICIES["notifications"]["retention_days"] == 90
        assert RETENTION_POLICIES["notifications"]["action"] == "delete"

    def test_activity_log_retention_365_days(self):
        assert RETENTION_POLICIES["activity_log"]["retention_days"] == 365
        assert RETENTION_POLICIES["activity_log"]["action"] == "anonymize"

    def test_expired_snapshots_immediate(self):
        assert RETENTION_POLICIES["expired_snapshots"]["retention_days"] == 0
        assert RETENTION_POLICIES["expired_snapshots"]["action"] == "revoke"

    def test_closed_applications_730_days(self):
        assert RETENTION_POLICIES["closed_applications"]["retention_days"] == 730
        assert RETENTION_POLICIES["closed_applications"]["action"] == "anonymize"

    def test_all_policies_have_required_keys(self):
        for name, policy in RETENTION_POLICIES.items():
            assert "retention_days" in policy, f"{name} missing retention_days"
            assert "action" in policy, f"{name} missing action"
            assert policy["action"] in ("delete", "anonymize", "revoke"), (
                f"{name} has invalid action: {policy['action']}"
            )


class TestConsentLogModel:
    def test_consent_types_defined(self):
        assert "passport_visibility" in CONSENT_TYPES
        assert "discoverable" in CONSENT_TYPES
        assert "pool_consent" in CONSENT_TYPES
        assert "outreach_response" in CONSENT_TYPES
        assert "deletion_request" in CONSENT_TYPES
        assert "data_export" in CONSENT_TYPES

    def test_consent_actions_defined(self):
        assert "granted" in CONSENT_ACTIONS
        assert "revoked" in CONSENT_ACTIONS
        assert "updated" in CONSENT_ACTIONS


class TestRetentionReport:
    def test_report_structure(self):
        from datetime import UTC, datetime

        report = RetentionReport(
            policy="notifications",
            records_affected=42,
            action="delete",
            cutoff_date=datetime.now(UTC),
        )
        assert report.policy == "notifications"
        assert report.records_affected == 42
        assert report.action == "delete"

    def test_report_immutable(self):
        from datetime import UTC, datetime

        report = RetentionReport(
            policy="test",
            records_affected=0,
            action="delete",
            cutoff_date=datetime.now(UTC),
        )
        try:
            report.policy = "changed"  # type: ignore[misc]
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass
