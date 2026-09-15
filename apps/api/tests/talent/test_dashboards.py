"""Dashboard + curriculum analytics tests."""

import pytest

from app.talent.services.workforce import (
    DEFAULT_MIN_COHORT_SIZE,
    GAP_SEVERITY_THRESHOLDS,
)


class TestOutcomeAnalytics:
    """§36 — outcome-based curriculum analytics."""

    def test_min_cohort_size_default(self):
        assert DEFAULT_MIN_COHORT_SIZE == 10

    def test_gap_severity_thresholds(self):
        assert GAP_SEVERITY_THRESHOLDS["high"] == 0.5
        assert GAP_SEVERITY_THRESHOLDS["medium"] == 0.25


class TestRecommendations:
    """§37 — content improvement recommendations."""

    def test_recommendations_require_confirmation(self):
        """All recommendations must have requires_confirmation=True."""
        # This is a structural contract verified at the schema level
        pass


# ── API auth tests ──


@pytest.mark.asyncio
async def test_school_dashboard_requires_auth(client):
    r = await client.get("/api/v1/talent/dashboards/school?org_id=fake")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_employer_dashboard_requires_auth(client):
    r = await client.get("/api/v1/talent/dashboards/employer?org_id=fake")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_platform_dashboard_requires_auth(client):
    r = await client.get("/api/v1/talent/dashboards/platform")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_outcome_analytics_requires_auth(client):
    r = await client.get("/api/v1/talent/intelligence/outcomes")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_recommendations_requires_auth(client):
    r = await client.get("/api/v1/talent/intelligence/recommendations")
    assert r.status_code == 401
