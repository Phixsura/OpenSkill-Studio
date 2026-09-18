"""Employer / opportunity tests — schema validation, auth checks."""

import pytest


@pytest.mark.asyncio
async def test_create_employer_requires_auth(client):
    response = await client.post("/api/v1/talent/employers/fake", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_employer_requires_auth(client):
    response = await client.get("/api/v1/talent/employers/fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_opportunity_requires_auth(client):
    response = await client.post("/api/v1/talent/opportunities?org_id=fake", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_opportunities_requires_auth(client):
    response = await client.get("/api/v1/talent/opportunities")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_opportunity_requires_auth(client):
    response = await client.get("/api/v1/talent/opportunities/fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_opportunity_requires_auth(client):
    response = await client.patch("/api/v1/talent/opportunities/fake", json={})
    assert response.status_code == 401
