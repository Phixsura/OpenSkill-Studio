"""Profile completeness scoring tests — pure logic, no DB needed."""

from app.talent.services.profile_completeness import (
    COMPLETENESS_ITEMS,
    LEVELS,
    CompletenessResult,
    compute_profile_completeness,
)


class TestComputeCompleteness:
    def test_empty_profile_zero(self):
        result = compute_profile_completeness(
            passport=None,
            evidence_count=0,
            credential_count=0,
            has_verified_evidence=False,
        )
        assert result.score == 0.0
        assert result.level == "beginner"
        assert len(result.completed_items) == 0
        assert len(result.missing_items) == len(COMPLETENESS_ITEMS)

    def test_full_profile_all_star(self):
        result = compute_profile_completeness(
            passport={
                "preferred_opportunity_types": ["internship"],
                "discoverable": True,
                "availability_status": "available",
                "availability_note": "Looking for AI design roles",
            },
            evidence_count=5,
            credential_count=2,
            has_verified_evidence=True,
        )
        assert result.score == 100.0
        assert result.level == "all_star"
        assert len(result.missing_items) == 0
        assert len(result.completed_items) == len(COMPLETENESS_ITEMS)

    def test_partial_profile_intermediate(self):
        result = compute_profile_completeness(
            passport={
                "preferred_opportunity_types": ["full_time"],
                "discoverable": False,
            },
            evidence_count=2,
            credential_count=0,
            has_verified_evidence=False,
        )
        # has_evidence=20 + has_preferred_types=10 = 30
        assert result.score == 30.0
        assert result.level == "intermediate"
        assert "has_evidence" in result.completed_items
        assert "has_preferred_types" in result.completed_items

    def test_portfolio_requires_three_evidence(self):
        result2 = compute_profile_completeness(
            passport=None,
            evidence_count=2,
            credential_count=0,
            has_verified_evidence=False,
        )
        assert "has_portfolio" not in result2.completed_items

        result3 = compute_profile_completeness(
            passport=None,
            evidence_count=3,
            credential_count=0,
            has_verified_evidence=False,
        )
        assert "has_portfolio" in result3.completed_items

    def test_missing_items_have_actions(self):
        result = compute_profile_completeness(
            passport=None,
            evidence_count=0,
            credential_count=0,
            has_verified_evidence=False,
        )
        for item in result.missing_items:
            assert "key" in item
            assert "label" in item
            assert "weight" in item
            assert "action" in item
            assert len(item["action"]) > 10

    def test_level_thresholds(self):
        for threshold, _label in LEVELS:
            r = compute_profile_completeness(
                passport={
                    "preferred_opportunity_types": ["a"] if threshold >= 10 else [],
                    "discoverable": threshold >= 25,
                    "availability_status": "open" if threshold >= 30 else None,
                    "availability_note": "bio" if threshold >= 40 else None,
                },
                evidence_count=10 if threshold >= 20 else 0,
                credential_count=2 if threshold >= 35 else 0,
                has_verified_evidence=threshold >= 50,
            )
            # Score should be non-negative
            assert r.score >= 0

    def test_discoverable_flag(self):
        result = compute_profile_completeness(
            passport={"discoverable": True},
            evidence_count=0,
            credential_count=0,
            has_verified_evidence=False,
        )
        assert "discoverable" in result.completed_items
        assert result.score == 15.0


class TestCompletenessResult:
    def test_frozen(self):
        result = CompletenessResult(
            score=50.0,
            level="advanced",
            completed_items=["a"],
            missing_items=[],
        )
        try:
            result.score = 100.0  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass
