"""Workforce intelligence tests — thresholds, gap severity, auth."""

import pytest

from app.talent.services.workforce import (
    DEFAULT_MIN_COHORT_SIZE,
    GAP_SEVERITY_THRESHOLDS,
)


class TestPrivacyThresholds:
    def test_default_min_cohort_size(self):
        assert DEFAULT_MIN_COHORT_SIZE == 10

    def test_min_cohort_size_is_positive(self):
        assert DEFAULT_MIN_COHORT_SIZE > 0


class TestGapSeverity:
    def test_thresholds(self):
        assert GAP_SEVERITY_THRESHOLDS["high"] == 0.5
        assert GAP_SEVERITY_THRESHOLDS["medium"] == 0.25

    def test_high_severity(self):
        """gap/demand > 0.5 → high."""
        ratio = 0.6
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "high"

    def test_medium_severity(self):
        """gap/demand > 0.25 but ≤ 0.5 → medium."""
        ratio = 0.35
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "medium"

    def test_low_severity(self):
        """gap/demand ≤ 0.25 → low."""
        ratio = 0.2
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "low"

    def test_zero_demand_is_low(self):
        """When demand = 0, ratio = 0 → low."""
        ratio = 0
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "low"

    def test_boundary_high(self):
        """Exactly 0.5 is NOT high (> not >=)."""
        ratio = 0.5
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "medium"

    def test_boundary_medium(self):
        """Exactly 0.25 is NOT medium (> not >=)."""
        ratio = 0.25
        if ratio > GAP_SEVERITY_THRESHOLDS["high"]:
            severity = "high"
        elif ratio > GAP_SEVERITY_THRESHOLDS["medium"]:
            severity = "medium"
        else:
            severity = "low"
        assert severity == "low"


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_demand_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/demand")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_supply_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/supply")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_gaps_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/gaps")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_coverage_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/coverage")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_placements_analytics_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/placements")
    assert response.status_code == 401
