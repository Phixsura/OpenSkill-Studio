"""Curriculum intelligence tests — coverage matrix structure, auth."""

import pytest

from app.talent.models.capability import MAPPING_SOURCE_TYPES


class TestCoverageMatrix:
    def test_mapping_source_types_cover_curriculum(self):
        """The mapping source types should cover all content types
        that contribute to curriculum coverage."""
        assert "skill" in MAPPING_SOURCE_TYPES
        assert "skill_pack" in MAPPING_SOURCE_TYPES
        assert "project_template" in MAPPING_SOURCE_TYPES
        assert "workflow_pack" in MAPPING_SOURCE_TYPES
        assert "assessment_blueprint" in MAPPING_SOURCE_TYPES

    def test_at_least_5_source_types(self):
        assert len(MAPPING_SOURCE_TYPES) >= 5


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_coverage_endpoint_requires_auth(client):
    response = await client.get("/api/v1/talent/intelligence/coverage")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_coverage_with_capability_filter(client):
    """Coverage endpoint supports capability_id filter — still requires auth."""
    response = await client.get(
        "/api/v1/talent/intelligence/coverage?capability_id=fake"
    )
    assert response.status_code == 401
