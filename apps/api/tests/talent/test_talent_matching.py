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
        import re

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
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""')
        ]
        code_only = "\n".join(code_lines)
        # Must NOT reference demographic fields in executable code
        for forbidden in ("date_of_birth", "sexual_orientation",
                          "political_belief", "marital_status"):
            assert forbidden not in code_only.lower(), (
                f"Protected attribute '{forbidden}' found in candidate query code"
            )


class TestEngineVersion:
    def test_version_format(self):
        parts = ENGINE_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_match_candidates_requires_auth(client):
    response = await client.post("/api/v1/talent/opportunities/fake/match")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_match_opportunities_requires_auth(client):
    response = await client.get("/api/v1/talent/opportunities/matches")
    assert response.status_code == 401
