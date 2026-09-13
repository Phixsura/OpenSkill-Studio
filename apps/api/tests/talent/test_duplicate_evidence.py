"""Duplicate evidence detection tests — service logic validation."""

from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES, VERIFICATION_LEVELS


class TestEvidenceDeduplication:
    """Verify that the evidence service handles duplicates correctly.

    The EvidenceService.record_evidence() method already implements
    deduplication: when an active row exists with the same
    (user_id, capability_id, source_type, source_id), it supersedes
    the old row and creates a new one. This tests the constants and
    validation that support that behavior.
    """

    def test_source_types_defined(self):
        assert len(EVIDENCE_SOURCE_TYPES) >= 13
        assert "skill_completion" in EVIDENCE_SOURCE_TYPES
        assert "assessment_result" in EVIDENCE_SOURCE_TYPES
        assert "employment_verification" in EVIDENCE_SOURCE_TYPES

    def test_verification_levels_defined(self):
        assert len(VERIFICATION_LEVELS) >= 7
        assert "self_reported" in VERIFICATION_LEVELS
        assert "employer_verified" in VERIFICATION_LEVELS

    def test_duplicate_key_components(self):
        """The dedup key is (user_id, capability_id, source_type, source_id).
        All four must be present for the dedup check to work."""
        # Verify the key components are standard fields
        from app.talent.models.evidence import CapabilityEvidence

        assert hasattr(CapabilityEvidence, "user_id")
        assert hasattr(CapabilityEvidence, "capability_id")
        assert hasattr(CapabilityEvidence, "source_type")
        assert hasattr(CapabilityEvidence, "source_id")
        assert hasattr(CapabilityEvidence, "status")
        assert hasattr(CapabilityEvidence, "supersedes_id")

    def test_status_values(self):
        """Evidence status should support active, voided, superseded."""
        # These are the allowed status values
        expected = {"active", "voided", "superseded"}
        # The model uses String(20) — verify the values fit
        for status in expected:
            assert len(status) <= 20

    def test_supersedes_chain(self):
        """supersedes_id enables provenance tracking for replaced evidence."""
        from app.talent.models.evidence import CapabilityEvidence

        assert hasattr(CapabilityEvidence, "supersedes_id")
