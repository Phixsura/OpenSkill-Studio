"""Talent matching tests — weights, consent gate, signal bounds, auth."""

import inspect

import pytest

from app.talent.services.talent_matching import (
    ENGINE_VERSION,
    TALENT_WEIGHTS,
    TalentMatchingService,
)


class TestTalentWeights:
    def test_weights_sum_to_1(self):
        total = sum(TALENT_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"

    def test_all_weights_positive(self):
        for signal, weight in TALENT_WEIGHTS.items():
            assert weight > 0, f"Weight for {signal} should be positive"
            assert weight <= 1, f"Weight for {signal} should be ≤ 1"

    def test_expected_signals_present(self):
        expected = {
            "capability_gap_score",
            "evidence_confidence",
            "evidence_recency",
            "portfolio_relevance",
            "credential_match",
        }
        assert set(TALENT_WEIGHTS.keys()) == expected

    def test_capability_gap_is_dominant(self):
        """Capability gap should be the strongest signal."""
        assert TALENT_WEIGHTS["capability_gap_score"] >= max(
            w for k, w in TALENT_WEIGHTS.items() if k != "capability_gap_score"
        )


class TestConsentGate:
    """Verify the matching service structurally excludes non-discoverable users.

    The consent gate is the most critical safety property: users who haven't
    opted into discoverability must NEVER appear in candidate results.
    """

    def test_consent_gate_in_match_candidates(self):
        """The match_candidates_for_opportunity method must query
        discoverable=true in its SQL. We verify by inspecting the source."""
        source = inspect.getsource(TalentMatchingService.match_candidates_for_opportunity)
        assert "discoverable" in source, (
            "match_candidates_for_opportunity must filter on discoverable"
        )

    def test_only_id_and_display_name_selected(self):
        """The candidate query must select ONLY id + display_name to
        structurally exclude protected attributes from the feature space."""

        source = inspect.getsource(TalentMatchingService.match_candidates_for_opportunity)
        # Must reference User.id and User.display_name
        assert "User.id" in source
        assert "User.display_name" in source
        # Strip comments and docstrings before checking for forbidden terms
        # (the docstring/comments legitimately mention protected attributes
        # as things we DON'T use — the check is on executable code)
        code_lines = [
            line
            for line in source.split("\n")
            if line.strip()
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
        ]
        code_only = "\n".join(code_lines)
        # Must NOT reference demographic fields in executable code
        for forbidden in (
            "date_of_birth",
            "sexual_orientation",
            "political_belief",
            "marital_status",
        ):
            assert forbidden not in code_only.lower(), (
                f"Protected attribute '{forbidden}' found in candidate query code"
            )


class TestEngineVersion:
    def test_version_format(self):
        parts = ENGINE_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ---- API auth tests ----


class TestAdjacencyCredit:
    """Adjacent skill inference — partial credit at graph distances 1 and 2."""

    def test_adjacency_credit_values(self):
        from app.talent.services.talent_matching import _ADJACENCY_CREDIT

        assert _ADJACENCY_CREDIT[1] == 0.5, "Distance 1 should give 50% credit"
        assert _ADJACENCY_CREDIT[2] == 0.25, "Distance 2 should give 25% credit"

    def test_adjacency_edge_types(self):
        from app.talent.services.talent_matching import _ADJACENCY_EDGE_TYPES

        expected = {"related_to", "commonly_paired_with", "specializes", "subsumes"}
        assert expected == _ADJACENCY_EDGE_TYPES

    def test_hard_constraints_relax_with_adjacent(self):
        """When user lacks cap X but has adjacent cap Y at min_level,
        the hard constraint is relaxed (no failure)."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        profile = {
            "cap_adjacent": {"level": 3, "score": 0.7, "confidence": 0.8},
        }
        required = [{"capability_id": "cap_required", "min_level": 2}]
        adjacency = {
            "cap_required": [("cap_adjacent", 1)],
        }
        failures = svc._check_hard_constraints(profile, required, adjacency=adjacency)
        assert failures == [], "Should relax constraint when adjacent skill meets level"

    def test_hard_constraints_fail_without_adjacency(self):
        """Without adjacency graph, missing cap should hard-fail."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        profile = {
            "cap_adjacent": {"level": 3, "score": 0.7, "confidence": 0.8},
        }
        required = [{"capability_id": "cap_required", "min_level": 2}]
        failures = svc._check_hard_constraints(profile, required, adjacency=None)
        assert len(failures) == 1
        assert failures[0]["code"] == "CAPABILITY_BELOW_REQUIRED"

    def test_hard_constraints_fail_adjacent_below_level(self):
        """Adjacent skill that doesn't meet min_level should still fail."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        profile = {
            "cap_adjacent": {"level": 1, "score": 0.3, "confidence": 0.5},
        }
        required = [{"capability_id": "cap_required", "min_level": 3}]
        adjacency = {
            "cap_required": [("cap_adjacent", 1)],
        }
        failures = svc._check_hard_constraints(profile, required, adjacency=adjacency)
        assert len(failures) == 1, "Adjacent skill below min_level should still fail"

    def test_hard_constraints_direct_match_preferred_over_adjacent(self):
        """When user has the direct capability, adjacency is not consulted."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        profile = {
            "cap_required": {"level": 3, "score": 0.7, "confidence": 0.8},
            "cap_adjacent": {"level": 5, "score": 0.9, "confidence": 0.9},
        }
        required = [{"capability_id": "cap_required", "min_level": 2}]
        adjacency = {
            "cap_required": [("cap_adjacent", 1)],
        }
        failures = svc._check_hard_constraints(profile, required, adjacency=adjacency)
        assert failures == []

    def test_explain_signals_generates_adjacent_reason(self):
        """Adjacent skill match should produce ADJACENT_SKILL reason chip."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        signals = {"capability_gap_score": 0.8}
        required = [{"capability_id": "cap_missing", "min_level": 2}]
        profile = {
            "cap_adj": {"level": 3, "score": 0.7},
        }
        adjacency = {
            "cap_missing": [("cap_adj", 1)],
        }
        reasons, _gaps = svc._explain_signals(signals, required, [], profile, adjacency=adjacency)
        adj_reasons = [r for r in reasons if r["code"] == "ADJACENT_SKILL"]
        assert len(adj_reasons) == 1
        assert adj_reasons[0]["adjacent_capability_id"] == "cap_adj"
        assert adj_reasons[0]["distance"] == 1

    def test_explain_signals_no_adjacent_when_directly_met(self):
        """No ADJACENT_SKILL reason when the capability is directly met."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        signals = {"capability_gap_score": 1.0}
        required = [{"capability_id": "cap_met", "min_level": 2}]
        profile = {
            "cap_met": {"level": 3, "score": 0.7},
            "cap_adj": {"level": 5, "score": 0.9},
        }
        adjacency = {
            "cap_met": [("cap_adj", 1)],
        }
        reasons, _gaps = svc._explain_signals(signals, required, [], profile, adjacency=adjacency)
        adj_reasons = [r for r in reasons if r["code"] == "ADJACENT_SKILL"]
        assert adj_reasons == [], "No adjacent reason when capability is directly met"

    def test_hard_constraints_distance_2_relaxation(self):
        """Distance-2 adjacent skill should also relax hard constraint."""
        svc = TalentMatchingService.__new__(TalentMatchingService)
        profile = {
            "cap_d2": {"level": 4, "score": 0.8, "confidence": 0.9},
        }
        required = [{"capability_id": "cap_required", "min_level": 2}]
        adjacency = {
            "cap_required": [("cap_d2", 2)],
        }
        failures = svc._check_hard_constraints(profile, required, adjacency=adjacency)
        assert failures == [], "Distance-2 adjacent skill should relax constraint"


class TestFairnessService:
    """Fairness metric computation — score distribution, HHI, spread."""

    def test_empty_results(self):
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        result = asyncio.run(svc.compute_fairness_metrics([]))
        assert result["status"] == "no_results"

    def test_all_excluded_results(self):
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [{"tier": "excluded", "score": 0.0}]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        assert result["status"] == "no_ranked_results"

    def test_score_distribution_single(self):
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [{"score": 0.8, "tier": "great", "signals": {"a": 0.8}}]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        assert result["status"] == "computed"
        dist = result["metrics"]["score_distribution"]
        assert dist["count"] == 1
        assert dist["mean"] == 0.8
        assert dist["median"] == 0.8
        assert dist["std"] == 0.0

    def test_score_distribution_multiple(self):
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [
            {"score": 0.2, "tier": "fair", "signals": {"a": 0.2}},
            {"score": 0.4, "tier": "fair", "signals": {"a": 0.4}},
            {"score": 0.6, "tier": "good", "signals": {"a": 0.6}},
            {"score": 0.8, "tier": "great", "signals": {"a": 0.8}},
        ]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        dist = result["metrics"]["score_distribution"]
        assert dist["count"] == 4
        assert dist["mean"] == 0.5
        assert dist["min"] == 0.2
        assert dist["max"] == 0.8

    def test_hhi_single_signal_high_concentration(self):
        """Single signal → HHI = 1.0 (maximum concentration)."""
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [
            {"score": 0.7, "tier": "good", "signals": {"gap": 0.7}},
            {"score": 0.5, "tier": "fair", "signals": {"gap": 0.5}},
        ]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        conc = result["metrics"]["signal_concentration"]
        assert conc["herfindahl_index"] == 1.0
        assert conc["interpretation"] == "high_concentration"

    def test_hhi_balanced_signals(self):
        """Evenly distributed signals → low HHI."""
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [
            {
                "score": 0.6,
                "tier": "good",
                "signals": {"a": 0.2, "b": 0.2, "c": 0.2, "d": 0.2, "e": 0.2},
            },
            {
                "score": 0.5,
                "tier": "fair",
                "signals": {"a": 0.2, "b": 0.2, "c": 0.2, "d": 0.2, "e": 0.2},
            },
        ]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        conc = result["metrics"]["signal_concentration"]
        assert conc["herfindahl_index"] == 0.2  # 5 × (0.2)^2
        assert conc["interpretation"] == "balanced"

    def test_rank_consistency_sorted(self):
        """Sorted scores should have zero violations."""
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [
            {"score": 0.9, "tier": "great", "signals": {}},
            {"score": 0.7, "tier": "good", "signals": {}},
            {"score": 0.5, "tier": "fair", "signals": {}},
        ]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        rc = result["metrics"]["rank_consistency"]
        assert rc["violations"] == 0
        assert rc["monotonicity"] == 1.0

    def test_excluded_count_reported(self):
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [
            {"score": 0.9, "tier": "great", "signals": {}},
            {"score": 0.0, "tier": "excluded", "signals": {}},
            {"score": 0.0, "tier": "excluded", "signals": {}},
        ]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        assert result["excluded_count"] == 2
        assert result["result_count"] == 1  # Only 1 non-excluded

    def test_score_spread_with_enough_results(self):
        """Score spread computed when ≥10 results."""
        import asyncio

        from app.talent.services.fairness import FairnessService

        svc = FairnessService.__new__(FairnessService)
        data = [{"score": i / 20.0, "tier": "fair", "signals": {}} for i in range(1, 21)]
        result = asyncio.run(svc.compute_fairness_metrics(data))
        spread = result["metrics"]["score_spread"]
        assert "top_10_mean" in spread
        assert "bottom_10_mean" in spread
        assert spread["top_10_mean"] > spread["bottom_10_mean"]


# ---- API auth tests ----


@pytest.mark.asyncio
async def test_match_candidates_requires_auth(client):
    response = await client.post("/api/v1/talent/opportunities/fake/match")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_match_opportunities_requires_auth(client):
    response = await client.get("/api/v1/talent/opportunities/matches")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_match_fairness_requires_auth(client):
    response = await client.post("/api/v1/talent/opportunities/fake/match/fairness")
    assert response.status_code == 401
