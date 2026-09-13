"""Evidence ledger tests — schema validation, immutability contracts."""

import pytest

from app.talent.models.evidence import (
    EVIDENCE_SOURCE_TYPES,
    VERIFICATION_LEVELS,
    VERIFICATION_WEIGHTS,
)


class TestEvidenceConstants:
    def test_source_types_complete(self):
        assert "skill_completion" in EVIDENCE_SOURCE_TYPES
        assert "employment_verification" in EVIDENCE_SOURCE_TYPES
        assert len(EVIDENCE_SOURCE_TYPES) == 13

    def test_verification_levels_ordered(self):
        # Highest trust first
        assert VERIFICATION_LEVELS[0] == "employer_verified"
        assert VERIFICATION_LEVELS[-1] == "self_reported"

    def test_weights_match_levels(self):
        for level in VERIFICATION_LEVELS:
            assert level in VERIFICATION_WEIGHTS

    def test_weights_ordered(self):
        weights = [VERIFICATION_WEIGHTS[level] for level in VERIFICATION_LEVELS]
        # Should be descending
        for i in range(len(weights) - 1):
            assert weights[i] >= weights[i + 1]

    def test_employer_verified_is_highest(self):
        assert VERIFICATION_WEIGHTS["employer_verified"] == 1.0

    def test_self_reported_is_lowest(self):
        assert VERIFICATION_WEIGHTS["self_reported"] == 0.3


# ---- API tests ----

@pytest.mark.asyncio
async def test_list_evidence_requires_auth(client):
    response = await client.get("/api/v1/talent/evidence")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_record_evidence_requires_auth(client):
    response = await client.post("/api/v1/talent/evidence", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_void_evidence_requires_auth(client):
    response = await client.post("/api/v1/talent/evidence/fake/void", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_provenance_requires_auth(client):
    response = await client.get("/api/v1/talent/evidence/fake/provenance")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_capability_profile_requires_auth(client):
    response = await client.get("/api/v1/talent/users/fake/profile")
    assert response.status_code == 401
