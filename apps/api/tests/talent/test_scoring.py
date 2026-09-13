"""Capability scoring engine tests — pure logic, no DB needed."""

from datetime import datetime, timezone, timedelta

import pytest

from app.talent.services.scoring import (
    SCORING_VERSION,
    compute_score_from_evidence,
    decay_factor,
    determine_level,
    DEFAULT_LEVEL_THRESHOLDS,
)


class TestDecayFactor:
    def test_no_config_returns_1(self):
        now = datetime.now(timezone.utc)
        assert decay_factor(now, now, None) == 1.0

    def test_no_half_life_key_returns_1(self):
        now = datetime.now(timezone.utc)
        assert decay_factor(now, now, {"other": 100}) == 1.0

    def test_zero_age_returns_1(self):
        now = datetime.now(timezone.utc)
        assert decay_factor(now, now, {"half_life_days": 365}) == 1.0

    def test_one_half_life_returns_half(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=365)
        result = decay_factor(past, now, {"half_life_days": 365})
        assert abs(result - 0.5) < 0.001

    def test_two_half_lives_returns_quarter(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=730)
        result = decay_factor(past, now, {"half_life_days": 365})
        assert abs(result - 0.25) < 0.001

    def test_fast_decay_90_days(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=90)
        result = decay_factor(past, now, {"half_life_days": 90})
        assert abs(result - 0.5) < 0.001

    def test_future_date_returns_1(self):
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=30)
        assert decay_factor(future, now, {"half_life_days": 365}) == 1.0

    def test_zero_half_life_returns_1(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=100)
        assert decay_factor(past, now, {"half_life_days": 0}) == 1.0


class TestComputeScore:
    def _make_evidence(self, **overrides):
        defaults = {
            "score_normalized": 0.8,
            "verification_level": "instructor_verified",
            "confidence": 1.0,
            "occurred_at": datetime.now(timezone.utc),
            "status": "active",
            "expires_at": None,
        }
        defaults.update(overrides)
        return defaults

    def test_empty_evidence(self):
        score, conf, sub = compute_score_from_evidence([], None, datetime.now(timezone.utc))
        assert score == 0.0
        assert conf == 0.0
        assert sub == 0

    def test_single_evidence(self):
        ev = [self._make_evidence()]
        score, conf, sub = compute_score_from_evidence(ev, None, datetime.now(timezone.utc))
        # With k=3 shrinkage: (1/(1+3)) * (0.8*0.85*1.0*1.0) + (3/(1+3)) * 0.5
        # = 0.25 * 0.68 + 0.75 * 0.5 = 0.17 + 0.375 = 0.545
        assert 0.5 < score < 0.6
        assert conf == 0.25  # 1 - (3/(1+3))
        assert sub == 1

    def test_many_evidence_converges(self):
        evs = [self._make_evidence() for _ in range(20)]
        score, conf, sub = compute_score_from_evidence(evs, None, datetime.now(timezone.utc))
        # With 20 items, shrinkage effect is small
        # raw = 0.8 * 0.85 = 0.68
        # shrunk ≈ (20/23) * 0.68 + (3/23) * 0.5 ≈ 0.591 + 0.065 ≈ 0.656
        assert score > 0.6
        assert conf > 0.85
        assert sub == 20

    def test_filters_inactive(self):
        evs = [
            self._make_evidence(status="active"),
            self._make_evidence(status="voided"),
            self._make_evidence(status="superseded"),
        ]
        score, conf, sub = compute_score_from_evidence(evs, None, datetime.now(timezone.utc))
        # Only 1 active
        assert conf == 0.25

    def test_filters_expired(self):
        evs = [
            self._make_evidence(expires_at=datetime.now(timezone.utc) - timedelta(days=1)),
        ]
        score, conf, sub = compute_score_from_evidence(evs, None, datetime.now(timezone.utc))
        assert score == 0.0

    def test_self_reported_low_weight(self):
        ev = [self._make_evidence(verification_level="self_reported")]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(timezone.utc))
        # 0.8 * 0.30 * 1.0 = 0.24 → shrunk lower
        assert score < 0.45

    def test_employer_verified_high_weight(self):
        ev = [self._make_evidence(verification_level="employer_verified")]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(timezone.utc))
        # 0.8 * 1.0 * 1.0 = 0.8 → shrunk: 0.25*0.8 + 0.75*0.5 = 0.575
        assert score > 0.55

    def test_null_score_uses_default(self):
        ev = [self._make_evidence(score_normalized=None)]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(timezone.utc))
        # Uses 0.8 default → same as explicit 0.8
        assert score > 0.0

    def test_substantial_evidence_count(self):
        evs = [
            self._make_evidence(verification_level="employer_verified"),
            self._make_evidence(verification_level="self_reported"),
            self._make_evidence(verification_level="peer_verified"),
        ]
        _, _, sub = compute_score_from_evidence(evs, None, datetime.now(timezone.utc))
        # employer_verified + peer_verified = 2 substantial
        assert sub == 2

    def test_decay_reduces_score(self):
        old = datetime.now(timezone.utc) - timedelta(days=365)
        ev = [self._make_evidence(occurred_at=old)]
        score_decayed, _, _ = compute_score_from_evidence(
            ev, {"half_life_days": 365}, datetime.now(timezone.utc)
        )
        ev_fresh = [self._make_evidence()]
        score_fresh, _, _ = compute_score_from_evidence(
            ev_fresh, {"half_life_days": 365}, datetime.now(timezone.utc)
        )
        assert score_decayed < score_fresh


class TestDetermineLevel:
    def test_no_evidence_level_0(self):
        level, label = determine_level(0.0, 0, None)
        assert level == 0
        assert label == "No evidence"

    def test_level_1_foundation(self):
        level, _ = determine_level(0.25, 1, None)
        assert level == 1

    def test_level_requires_both_score_and_evidence(self):
        # High score but not enough evidence
        level, _ = determine_level(0.95, 2, None)
        assert level == 1  # Only 2 substantial evidence, can't reach L2 (needs 3)

    def test_level_5_expert(self):
        level, _ = determine_level(0.95, 15, None)
        assert level == 5

    def test_custom_definitions(self):
        custom = {
            "0": {"label": "None", "min_score": 0.0, "min_evidence": 0},
            "1": {"label": "Beginner", "min_score": 0.3, "min_evidence": 2},
        }
        level, label = determine_level(0.35, 3, custom)
        assert level == 1
        assert label == "Beginner"

    def test_scoring_version_is_set(self):
        assert SCORING_VERSION == "1.0.0"
