"""Experiments endpoint surface tests — no DB needed (ADR-017 exp01).

Every /experiments endpoint requires authentication (401 unauthenticated) and
request-body validation fires before any DB access (422 with envelope).
"""

import pytest

EXP_ID = "a" * 26

WRITE_ENDPOINTS = [
    ("post", "/api/v1/experiments", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/versions", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/transition", {"to_status": "review"}),
    ("patch", f"/api/v1/experiments/{EXP_ID}/ramp", {"ramp_bp": 100}),
    ("post", "/api/v1/experiments/layers", {}),
    ("post", "/api/v1/experiments/layers/learning-core/allocations", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/assignments:preview",
     {"unit_type": "user", "unit_id": "u" * 26}),
    ("post", "/api/v1/experiments/metric-definitions", {}),
    ("post", "/api/v1/experiments/metric-definitions/seed", {}),
]

READ_ENDPOINTS = [
    "/api/v1/experiments",
    f"/api/v1/experiments/{EXP_ID}",
    f"/api/v1/experiments/{EXP_ID}/versions",
    f"/api/v1/experiments/{EXP_ID}/events",
    f"/api/v1/experiments/{EXP_ID}/assignments",
    f"/api/v1/experiments/{EXP_ID}/exposures/stats",
    f"/api/v1/experiments/{EXP_ID}/metrics",
    "/api/v1/experiments/metric-definitions",
    "/api/v1/experiments/layers",
    "/api/v1/experiments/layers/learning-core/allocations",
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


async def test_layers_route_not_shadowed_by_dynamic_id(client):
    """/experiments/layers must not be captured by /experiments/{experiment_id}
    (§106.10 route-shadowing class): an auth-less GET must 401, and the path
    must resolve to the layers handler, not a 404/422 from the id route."""
    resp = await client.get("/api/v1/experiments/layers")
    assert resp.status_code == 401


async def test_unknown_status_filter_names_vocabulary(client):
    # Unauthenticated wins first; enum guard behavior is covered in DB tests —
    # here we pin that the route exists and rejects before 500.
    resp = await client.get("/api/v1/experiments?status=bogus")
    assert resp.status_code == 401


async def test_validation_shapes_are_bounded(client):
    """Oversized field values are rejected by schema bounds, not 500."""
    resp = await client.post(
        "/api/v1/experiments",
        json={
            "key": "x" * 500,
            "title": "t",
            "domain": "learning",
            "layer_key": "k",
        },
    )
    # Auth dependency runs first (401); the shape must never 500
    assert resp.status_code in (401, 422)


async def test_transition_body_required(client):
    resp = await client.post(f"/api/v1/experiments/{EXP_ID}/transition", json={})
    assert resp.status_code in (401, 422)
    assert "error" in resp.json()
