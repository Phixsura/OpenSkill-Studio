"""Capability ontology API tests — schema validation, graph semantics."""

import pytest

from app.talent.models.capability import EDGE_TYPES, MAPPING_SOURCE_TYPES
from app.talent.services.capability import slugify


class TestSlugify:
    def test_simple(self):
        assert slugify("AI Product Visual Design") == "ai-product-visual-design"

    def test_special_chars(self):
        assert slugify("Prompt Structuring (Advanced)") == "prompt-structuring-advanced"

    def test_underscores(self):
        assert slugify("image_to_video") == "image-to-video"

    def test_multiple_spaces(self):
        assert slugify("  Client  Brief  ") == "client-brief"


class TestEdgeTypes:
    def test_all_types_present(self):
        expected = {"requires", "related_to", "specializes", "subsumes", "commonly_paired_with"}
        assert expected == EDGE_TYPES


class TestMappingSourceTypes:
    def test_all_types_present(self):
        expected = {
            "skill",
            "skill_pack",
            "project_template",
            "workflow_pack",
            "rubric_criterion",
            "assessment_blueprint",
            "commercial_project",
        }
        assert expected == MAPPING_SOURCE_TYPES


# ---- API tests ----


@pytest.mark.asyncio
async def test_create_capability_missing_fields(client):
    response = await client.post("/api/v1/talent/capabilities", json={})
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_list_capabilities_requires_auth(client):
    response = await client.get("/api/v1/talent/capabilities")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_capability_validation(client):
    # No auth → 401
    response = await client.post(
        "/api/v1/talent/capabilities",
        json={"canonical_name": "", "category": "test"},
    )
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_edge_requires_auth(client):
    response = await client.post("/api/v1/talent/capabilities/fake/edges", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_graph_requires_auth(client):
    response = await client.get("/api/v1/talent/capabilities/fake/graph")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_mapping_requires_auth(client):
    response = await client.post("/api/v1/talent/capabilities/mappings", json={})
    assert response.status_code == 401
