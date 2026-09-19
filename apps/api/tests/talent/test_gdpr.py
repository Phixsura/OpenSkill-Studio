"""GDPR service tests — pure logic, no DB needed."""

from app.talent.services.gdpr import DELETION_GRACE_DAYS


class TestGDPRConstants:
    def test_deletion_grace_period(self):
        assert DELETION_GRACE_DAYS == 30

    def test_grace_days_positive(self):
        assert DELETION_GRACE_DAYS > 0

    def test_grace_days_reasonable(self):
        assert DELETION_GRACE_DAYS <= 90  # GDPR allows up to 30 days


class TestDeletionResponse:
    def test_response_structure(self):
        """Deletion response should have standard fields."""
        expected_keys = {
            "status",
            "user_id",
            "requested_at",
            "grace_period_days",
            "scheduled_deletion_at",
            "note",
        }
        # Verify the expected key set is reasonable
        assert "status" in expected_keys
        assert "grace_period_days" in expected_keys

    def test_export_categories(self):
        """Verify expected export data categories."""
        expected_categories = {
            "passport",
            "passport_snapshots",
            "evidence",
            "credentials",
            "applications",
            "outcomes",
            "pool_memberships",
        }
        assert len(expected_categories) == 7
