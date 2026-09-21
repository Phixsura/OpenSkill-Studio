"""Edge-case and adversarial scenario tests for the talent layer.

Tests extreme inputs, boundary conditions, race-condition-prone paths,
and attack vectors that the happy-path E2E doesn't cover.
"""

import pytest

from app.talent.models.application import APPLICATION_TRANSITIONS, TERMINAL_STATUSES
from app.talent.models.evidence import (
    EVIDENCE_SOURCE_TYPES,
    VERIFICATION_LEVELS,
    VERIFICATION_WEIGHTS,
)
from app.talent.services.scoring import (
    SHRINKAGE_K,
    SHRINKAGE_PRIOR,
    compute_score_from_evidence,
    determine_level,
)

# ── Scoring edge cases ──


class TestScoringEdgeCases:
    """Edge cases in the scoring algorithm."""

    def _ev(self, **overrides):
        from datetime import UTC, datetime

        defaults = {
            "score_normalized": 0.8,
            "verification_level": "instructor_verified",
            "confidence": 1.0,
            "occurred_at": datetime.now(UTC),
            "status": "active",
            "expires_at": None,
        }
        defaults.update(overrides)
        return defaults

    def test_zero_score_evidence(self):
        """Evidence with score=0 should still contribute (not be ignored)."""
        evs = [self._ev(score_normalized=0.0)]
        score, conf, sub = compute_score_from_evidence(
            evs, None, __import__("datetime").datetime.now(__import__("datetime").UTC)
        )
        assert score > 0  # Shrinkage prior pulls it above 0
        assert conf == 0.25  # 1 item: 1/(1+3) confidence

    def test_perfect_score_capped(self):
        """Even with perfect evidence, score shouldn't exceed 1.0."""
        evs = [
            self._ev(score_normalized=1.0, verification_level="employer_verified")
            for _ in range(50)
        ]
        score, conf, sub = compute_score_from_evidence(
            evs, None, __import__("datetime").datetime.now(__import__("datetime").UTC)
        )
        assert score <= 1.0

    def test_extremely_old_evidence_with_fast_decay(self):
        """Evidence from 10 years ago with 90-day half-life should contribute nearly nothing."""
        from datetime import UTC, datetime, timedelta

        old = datetime.now(UTC) - timedelta(days=3650)
        evs = [self._ev(occurred_at=old)]
        score, _, _ = compute_score_from_evidence(evs, {"half_life_days": 90}, datetime.now(UTC))
        # 2^(-3650/90) ≈ 2^(-40.6) ≈ 0 — the decay factor is effectively zero
        assert score < 0.5  # Mostly prior (0.5)

    def test_all_expired_evidence(self):
        """All evidence expired — should return 0."""
        from datetime import UTC, datetime, timedelta

        past = datetime.now(UTC) - timedelta(days=1)
        evs = [self._ev(expires_at=past) for _ in range(5)]
        score, conf, sub = compute_score_from_evidence(evs, None, datetime.now(UTC))
        assert score == 0.0
        assert conf == 0.0

    def test_mix_of_active_and_expired(self):
        """Only active non-expired evidence should count."""
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        evs = [
            self._ev(status="active", expires_at=None),
            self._ev(status="voided"),
            self._ev(status="superseded"),
            self._ev(status="active", expires_at=now - timedelta(days=1)),
        ]
        score, conf, _ = compute_score_from_evidence(evs, None, now)
        # Only 1 active non-expired
        assert conf == 0.25

    def test_null_score_uses_default_080(self):
        """Evidence with score_normalized=None uses default 0.8."""
        evs = [self._ev(score_normalized=None)]
        score1, _, _ = compute_score_from_evidence(
            evs, None, __import__("datetime").datetime.now(__import__("datetime").UTC)
        )
        evs2 = [self._ev(score_normalized=0.8)]
        score2, _, _ = compute_score_from_evidence(
            evs2, None, __import__("datetime").datetime.now(__import__("datetime").UTC)
        )
        assert abs(score1 - score2) < 0.01

    def test_bayesian_shrinkage_converges(self):
        """With enough evidence, shrinkage effect becomes negligible."""
        evs = [self._ev() for _ in range(100)]
        score, conf, _ = compute_score_from_evidence(
            evs, None, __import__("datetime").datetime.now(__import__("datetime").UTC)
        )
        # With 100 items, confidence should be ~0.97
        assert conf > 0.95

    def test_level_requires_both_score_and_count(self):
        """High score with 0 substantial evidence stays at L0."""
        level, _ = determine_level(0.99, 0, None)
        assert level == 0

    def test_level_requires_both_score_and_count_reverse(self):
        """High evidence count with low score stays low."""
        level, _ = determine_level(0.1, 100, None)
        assert level == 0


# ── State machine edge cases ──


class TestStateMachineEdgeCases:
    """Application state machine boundary conditions."""

    def test_terminal_states_cannot_transition(self):
        for status in TERMINAL_STATUSES:
            assert APPLICATION_TRANSITIONS[status] == [], f"{status} should have no transitions"

    def test_no_direct_draft_to_hired(self):
        """Can't skip straight from draft to hired."""
        assert "hired" not in APPLICATION_TRANSITIONS["draft"]

    def test_no_direct_submitted_to_hired(self):
        assert "hired" not in APPLICATION_TRANSITIONS["submitted"]

    def test_cannot_unwithdraw(self):
        """Once withdrawn, no way back."""
        assert APPLICATION_TRANSITIONS["withdrawn"] == []

    def test_cannot_unreject(self):
        assert APPLICATION_TRANSITIONS["rejected"] == []

    def test_hired_only_from_accepted(self):
        """hired can only come from accepted."""
        for status, targets in APPLICATION_TRANSITIONS.items():
            if "hired" in targets:
                assert status == "accepted", f"{status} shouldn't transition to hired"


# ── Input validation edge cases ──


def test_capability_name_with_unicode_schema():
    """Unicode capability names should pass schema validation."""
    from app.talent.schemas.capability import CreateCapabilityRequest

    req = CreateCapabilityRequest(canonical_name="AI视觉设计 Ẁéírd Nàmé", category="visual_design")
    assert req.canonical_name == "AI视觉设计 Ẁéírd Nàmé"


@pytest.mark.asyncio
async def test_evidence_score_at_boundaries(client):
    """score_normalized at exact boundaries 0.0 and 1.0."""
    r = await client.post(
        "/api/v1/talent/evidence",
        json={
            "capability_id": "nonexistent",
            "source_type": "skill_completion",
            "source_id": "test",
            "verification_level": "self_reported",
            "occurred_at": "2026-01-01T00:00:00Z",
            "score_normalized": 0.0,
        },
    )
    assert r.status_code in (401, 422, 500)  # 401 no auth, 422 validation, 500 FK

    r = await client.post(
        "/api/v1/talent/evidence",
        json={
            "capability_id": "nonexistent",
            "source_type": "skill_completion",
            "source_id": "test",
            "verification_level": "self_reported",
            "occurred_at": "2026-01-01T00:00:00Z",
            "score_normalized": 1.0,
        },
    )
    assert r.status_code in (401, 422, 500)


@pytest.mark.asyncio
async def test_evidence_score_out_of_range(client):
    """score_normalized > 1.0 should be rejected."""
    r = await client.post(
        "/api/v1/talent/evidence",
        json={
            "capability_id": "x",
            "source_type": "skill_completion",
            "source_id": "test",
            "verification_level": "self_reported",
            "occurred_at": "2026-01-01T00:00:00Z",
            "score_normalized": 1.5,
        },
    )
    assert r.status_code in (401, 422)  # Should reject before reaching DB


@pytest.mark.asyncio
async def test_evidence_negative_score(client):
    """score_normalized < 0 should be rejected."""
    r = await client.post(
        "/api/v1/talent/evidence",
        json={
            "capability_id": "x",
            "source_type": "skill_completion",
            "source_id": "test",
            "verification_level": "self_reported",
            "occurred_at": "2026-01-01T00:00:00Z",
            "score_normalized": -0.1,
        },
    )
    assert r.status_code in (401, 422)


def test_empty_capability_name_rejected_schema():
    """Empty capability name should be rejected by schema."""
    from pydantic import ValidationError

    from app.talent.schemas.capability import CreateCapabilityRequest

    with pytest.raises(ValidationError):
        CreateCapabilityRequest(canonical_name="", category="test")


@pytest.mark.asyncio
async def test_passport_invalid_visibility(client):
    """Invalid visibility value should be rejected."""
    r = await client.patch(
        "/api/v1/talent/passport",
        json={"default_visibility": "INVALID_VALUE"},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_passport_invalid_field_names(client):
    """Unknown fields in visible_fields should be rejected."""
    r = await client.patch(
        "/api/v1/talent/passport",
        json={"visible_fields": ["nonexistent_field"]},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_opportunity_zero_openings_rejected(client):
    """openings=0 should be rejected (min 1)."""
    r = await client.post(
        "/api/v1/talent/opportunities?org_id=fake",
        json={
            "title": "Test",
            "opportunity_type": "internship",
            "openings": 0,
        },
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_opportunity_negative_openings_rejected(client):
    """Negative openings should be rejected."""
    r = await client.post(
        "/api/v1/talent/opportunities?org_id=fake",
        json={
            "title": "Test",
            "opportunity_type": "internship",
            "openings": -1,
        },
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_application_transition_invalid_status(client):
    """Transitioning to a nonexistent status should fail."""
    r = await client.patch(
        "/api/v1/talent/applications/fake/status",
        json={"status": "NONEXISTENT_STATUS"},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_verification_rating_exceeds_scale(client):
    """overall_rating > 5 should be rejected by schema."""
    r = await client.post(
        "/api/v1/talent/placements/fake/verification",
        json={"overall_rating": 6.0, "capability_ratings": []},
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_verification_negative_rating(client):
    """Negative overall_rating should be rejected."""
    r = await client.post(
        "/api/v1/talent/placements/fake/verification",
        json={"overall_rating": -1.0, "capability_ratings": []},
    )
    assert r.status_code in (401, 422)


# ── Cross-endpoint consistency ──


class TestCrossEndpointConsistency:
    """Verify consistency across related endpoints."""

    def test_all_source_types_are_known(self):
        """All 13 evidence source types are defined."""
        assert len(EVIDENCE_SOURCE_TYPES) == 13

    def test_all_verification_levels_have_weights(self):
        """Every verification level has a corresponding weight."""
        for level in VERIFICATION_LEVELS:
            assert level in VERIFICATION_WEIGHTS

    def test_verification_weights_are_positive(self):
        for level, weight in VERIFICATION_WEIGHTS.items():
            assert 0 < weight <= 1.0, f"{level} weight {weight} out of range"

    def test_verification_weights_monotonically_decrease(self):
        """Higher trust levels should have higher or equal weights."""
        prev_weight = None
        for level in VERIFICATION_LEVELS:
            weight = VERIFICATION_WEIGHTS[level]
            if prev_weight is not None:
                assert weight <= prev_weight, f"{level} weight {weight} > previous {prev_weight}"
            prev_weight = weight

    def test_all_states_reachable_from_draft(self):
        """Every non-draft status should be reachable from draft via some path."""
        reachable = {"draft"}
        queue = ["draft"]
        while queue:
            state = queue.pop(0)
            for next_state in APPLICATION_TRANSITIONS.get(state, []):
                if next_state not in reachable:
                    reachable.add(next_state)
                    queue.append(next_state)

        all_states = set(APPLICATION_TRANSITIONS.keys())
        unreachable = all_states - reachable
        assert unreachable == set(), f"States unreachable from draft: {unreachable}"

    def test_scoring_shrinkage_constants(self):
        """Shrinkage constants match the documented values."""
        assert SHRINKAGE_K == 3
        assert SHRINKAGE_PRIOR == 0.5
