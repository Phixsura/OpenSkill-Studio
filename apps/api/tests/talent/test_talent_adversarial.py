"""Adversarial invariant tests — safety, privacy, structural guarantees (ADR-015 D15/D17).

These tests verify structural properties that MUST hold regardless of
database state or user actions.
"""

import inspect

import pytest

from app.talent.models.application import (
    APPLICATION_TRANSITIONS,
    Application,
    ApplicationEvent,
)
from app.talent.models.evidence import CapabilityEvidence, VERIFICATION_WEIGHTS
from app.talent.models.passport import SkillPassport
from app.talent.services.scoring import SCORING_VERSION


class TestNoAutoHire:
    """Invariant: No Application transition to offer/rejected/hired without acted_by."""

    def test_application_event_acted_by_not_nullable(self):
        """The acted_by column on ApplicationEvent is NOT nullable.
        This structurally prevents any transition without an authenticated actor."""
        col = ApplicationEvent.__table__.columns["acted_by"]
        assert col.nullable is False, "acted_by must NOT be nullable"

    def test_no_state_auto_transitions_to_hired(self):
        """Only 'accepted' can transition to 'hired'. No other state can."""
        for status, targets in APPLICATION_TRANSITIONS.items():
            if status != "accepted":
                assert "hired" not in targets, f"State '{status}' can transition to 'hired'"

    def test_no_state_auto_transitions_to_offer(self):
        """Only interview/assessment can transition to offer."""
        allowed_offer_sources = {"interview", "assessment"}
        for status, targets in APPLICATION_TRANSITIONS.items():
            if "offer" in targets:
                assert status in allowed_offer_sources, (
                    f"State '{status}' can transition to 'offer' — "
                    "only interview/assessment should be able to"
                )


class TestEvidenceImmutability:
    """Invariant: CapabilityEvidence rows are append-only."""

    def test_evidence_has_status_column(self):
        """Status column exists for active/superseded/voided transitions."""
        assert "status" in CapabilityEvidence.__table__.columns

    def test_evidence_has_supersedes_id(self):
        """Corrections link to the superseded row, not mutation."""
        assert "supersedes_id" in CapabilityEvidence.__table__.columns

    def test_evidence_has_idempotency_index(self):
        """Partial unique index prevents duplicate active evidence."""
        indexes = {idx.name for idx in CapabilityEvidence.__table__.indexes}
        assert "uq_cap_evidence_idempotent" in indexes


class TestPassportPrivateByDefault:
    """Invariant: Passport is private by default, discoverable is opt-in."""

    def test_default_visibility_is_private(self):
        col = SkillPassport.__table__.columns["default_visibility"]
        assert col.server_default is not None
        assert "private" in str(col.server_default.arg)

    def test_discoverable_default_false(self):
        col = SkillPassport.__table__.columns["discoverable"]
        assert col.server_default is not None
        assert "false" in str(col.server_default.arg)


class TestProtectedAttributeExclusion:
    """Invariant: Protected attributes are structurally absent from talent matching.

    This tests the model definitions to ensure they don't store demographic/
    protected attributes that could leak into matching.
    """

    PROTECTED_COLUMN_NAMES = {
        "race", "ethnicity", "gender", "sex", "religion", "political",
        "sexual_orientation", "disability", "health", "age", "date_of_birth",
        "national_origin", "marital_status",
    }

    def test_evidence_no_protected_columns(self):
        columns = set(CapabilityEvidence.__table__.columns.keys())
        leaked = columns & self.PROTECTED_COLUMN_NAMES
        assert not leaked, f"CapabilityEvidence has protected columns: {leaked}"

    def test_passport_no_protected_columns(self):
        columns = set(SkillPassport.__table__.columns.keys())
        leaked = columns & self.PROTECTED_COLUMN_NAMES
        assert not leaked, f"SkillPassport has protected columns: {leaked}"

    def test_application_no_protected_columns(self):
        columns = set(Application.__table__.columns.keys())
        leaked = columns & self.PROTECTED_COLUMN_NAMES
        assert not leaked, f"Application has protected columns: {leaked}"


class TestScoringVersioned:
    """Invariant: Scoring algorithm is versioned and reproducible."""

    def test_scoring_version_format(self):
        parts = SCORING_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_verification_weights_sum_properties(self):
        """Verification weights are ordered and bounded."""
        values = list(VERIFICATION_WEIGHTS.values())
        assert all(0 < w <= 1.0 for w in values)
        assert max(values) == 1.0  # employer_verified
        assert min(values) == 0.3  # self_reported


class TestSnapshotIntegrity:
    """Invariant: PassportSnapshot payload is checksummed."""

    def test_snapshot_has_checksum_column(self):
        from app.talent.models.passport import PassportSnapshot
        assert "checksum" in PassportSnapshot.__table__.columns

    def test_snapshot_has_status_for_revocation(self):
        from app.talent.models.passport import PassportSnapshot
        assert "status" in PassportSnapshot.__table__.columns
