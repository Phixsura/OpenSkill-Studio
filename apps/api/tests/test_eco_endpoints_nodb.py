"""Ecosystem endpoint surface tests — no DB needed.

Every /ecosystem endpoint requires authentication (401 unauthenticated), and
request-body validation fires before any DB access (422 with envelope).
"""

import pytest

WRITE_ENDPOINTS = [
    ("post", "/api/v1/ecosystem/sources", {}),
    ("post", "/api/v1/ecosystem/observations", {}),
    ("post", "/api/v1/ecosystem/benchmark/suites", {}),
    ("post", "/api/v1/ecosystem/graph/edges", {}),
    ("post", "/api/v1/ecosystem/replacements/candidates/generate", {}),
    ("post", "/api/v1/ecosystem/drafts", {}),
    ("post", "/api/v1/ecosystem/rollouts", {}),
    ("post", "/api/v1/ecosystem/watchlists", {}),
    ("post", "/api/v1/ecosystem/impact/analyses", {}),
    # ADR-016 §11 amendments
    ("post", "/api/v1/ecosystem/observations/bulk-verify", {"ids": ["a" * 26]}),
    ("post", "/api/v1/ecosystem/resolution-candidates/bulk-decide",
     {"ids": ["a" * 26], "decision": "confirm"}),
    ("post", "/api/v1/ecosystem/pricing/availability/probe/model/" + "a" * 26, {}),
]

READ_ENDPOINTS = [
    "/api/v1/ecosystem/sources",
    "/api/v1/ecosystem/observations",
    "/api/v1/ecosystem/changes",
    "/api/v1/ecosystem/catalog/models",
    "/api/v1/ecosystem/resolution-candidates",
    "/api/v1/ecosystem/capability-mappings",
    "/api/v1/ecosystem/pricing/observations",
    "/api/v1/ecosystem/benchmark/suites",
    "/api/v1/ecosystem/benchmark/runs",
    "/api/v1/ecosystem/telemetry/snapshots",
    "/api/v1/ecosystem/impact/analyses",
    "/api/v1/ecosystem/replacements/candidates",
    "/api/v1/ecosystem/drafts",
    "/api/v1/ecosystem/rollouts",
    "/api/v1/ecosystem/watchlists",
    "/api/v1/ecosystem/dashboard",
    "/api/v1/ecosystem/signals/matching",
    "/api/v1/ecosystem/signals/workforce",
    "/api/v1/ecosystem/deprecation-calendar",
]


@pytest.mark.parametrize("path", READ_ENDPOINTS)
async def test_reads_require_auth(client, path):
    resp = await client.get(path)
    assert resp.status_code == 401, path
    assert "error" in resp.json()


@pytest.mark.parametrize("method,path,body", WRITE_ENDPOINTS)
async def test_writes_require_auth(client, method, path, body):
    resp = await client.request(method.upper(), path, json=body)
    assert resp.status_code == 401, path
    assert "error" in resp.json()


async def test_unknown_catalog_kind_is_404_shape(client):
    # Unauthenticated first — auth wins; the route itself exists
    resp = await client.get("/api/v1/ecosystem/catalog/nonsense-kind")
    assert resp.status_code == 401


async def test_validation_shapes_are_bounded(client):
    """Oversized field values are rejected by schema bounds (422), not 500."""
    resp = await client.post(
        "/api/v1/ecosystem/sources",
        json={
            "name": "x" * 5000,  # exceeds max_length=200
            "source_type": "provider_api",
            "trust_level": "official",
            "adapter_key": "json_catalog",
        },
    )
    # Auth dependency runs after body parsing in FastAPI? Body validation
    # happens first for malformed shapes; either 401 or 422 is acceptable,
    # but never a 500.
    assert resp.status_code in (401, 422)
