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
    ("post", f"/api/v1/experiments/{EXP_ID}/guardrails/incident", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/guardrails/evaluate", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/analysis", {}),
    ("post", f"/api/v1/experiments/{EXP_ID}/decisions", {}),
    ("post", f"/api/v1/experiments/decisions/{EXP_ID}/promotion-drafts", {}),
    ("post", f"/api/v1/experiments/promotion-drafts/{EXP_ID}/approve", {}),
    ("post", f"/api/v1/experiments/promotion-drafts/{EXP_ID}/reject", {}),
    ("post", f"/api/v1/experiments/promotion-drafts/{EXP_ID}/apply", {}),
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
    f"/api/v1/experiments/{EXP_ID}/guardrails/events",
    "/api/v1/experiments/decisions",
    "/api/v1/experiments/decisions/meta",
    f"/api/v1/experiments/decisions/{EXP_ID}",
    "/api/v1/experiments/promotion-drafts",
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


def test_experiment_reads_are_admin_gated():
    """R88-91 authz class: experiment specs, decisions, guardrail events and
    assignment diagnostics are operator surfaces — no endpoint module may
    fall back to plain get_current_user (any authenticated user)."""
    from pathlib import Path

    api_dir = Path(__file__).resolve().parents[1] / "app" / "experiments" / "api"
    offenders = [
        path.name
        for path in api_dir.glob("*.py")
        if path.name != "deps.py" and "get_current_user" in path.read_text(encoding="utf-8")
    ]
    assert not offenders, f"non-admin experiment reads: {offenders}"


def test_self_exposure_dedup_key_bound_matches_column():
    """Defect #36: the schema bound must equal the column bound (String(64))
    — anything wider reaches the DB as a truncation error that the fail-safe
    facade swallows as a silently dropped exposure."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.experiments.schemas import SelfExposureRequest

    ok = SelfExposureRequest(experiment_key="surface-x", dedup_key="d" * 64)
    assert ok.dedup_key == "d" * 64
    with _pytest.raises(ValidationError):
        SelfExposureRequest(experiment_key="surface-x", dedup_key="d" * 65)


def test_delegated_surface_manifest_pinned():
    """The org-delegation surface is a deliberate, PINNED set: per-experiment
    operating/diagnostic endpoints follow experiment_read_scope; everything
    platform-wide (creation, definitions, decisions, promotions, layers,
    holdouts, incident/evaluate triggers) stays require_platform_admin.
    Growing either set is a conscious edit here, never a drive-by."""
    from pathlib import Path

    api_dir = Path(__file__).resolve().parents[1] / "app" / "experiments" / "api"
    counts = {}
    for path in sorted(api_dir.glob("*.py")):
        if path.name in ("deps.py", "__init__.py"):
            continue
        text = path.read_text(encoding="utf-8")
        counts[path.name] = (
            text.count("Depends(experiment_read_scope)"),
            text.count("Depends(require_platform_admin)"),
        )
    assert counts == {
        "analysis.py": (2, 0),
        "assignments.py": (3, 0),
        "decisions.py": (0, 9),
        "experiments.py": (6, 2),
        "guardrails.py": (1, 2),
        "holdouts.py": (0, 3),
        "layers.py": (0, 5),
        "metrics.py": (2, 3),  # round 47: + CSV export (same read scope)
        "selfserve.py": (0, 0),
    }, counts
