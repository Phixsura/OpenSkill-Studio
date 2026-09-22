"""Round-32 tests (ADR-016 §39): HTTP-layer authz matrix + response contract.

The recurring authz classes (403-vs-404 oracles, missing owner gates, role
gates) are only provable at the HTTP layer — service tests never exercise
dependency wiring. This suite pins: anonymous → 401 everywhere; member → 403
on admin-only surfaces; member reads → 200 with the {data: ...} envelope;
errors → {error: {code, message}} shape.
"""

from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.main import app
from tests.test_eco_services_db import _mk_user

# Read surfaces any authenticated member may use
MEMBER_READ_PATHS = [
    "/api/v1/ecosystem/dashboard",
    "/api/v1/ecosystem/dashboard/coverage",
    "/api/v1/ecosystem/dashboard/trending",
    "/api/v1/ecosystem/catalog/models",
    "/api/v1/ecosystem/changes",
    "/api/v1/ecosystem/benchmark/leaderboard",
    "/api/v1/ecosystem/benchmark/runs",
    "/api/v1/ecosystem/security/advisories",
    "/api/v1/ecosystem/watchlists",
    "/api/v1/ecosystem/pricing/observations",
    "/api/v1/ecosystem/deprecation-calendar",
]

# Platform-admin-only surfaces (member must see 403, never data)
ADMIN_ONLY = [
    ("GET", "/api/v1/ecosystem/audit", None),
    ("GET", "/api/v1/ecosystem/audit.csv", None),
    ("GET", "/api/v1/ecosystem/catalog/models/duplicates", None),
    ("POST", "/api/v1/ecosystem/sources", {"name": "x", "source_type": "vendor_api",
                                           "trust_level": "official", "adapter_key": "manual"}),
    ("POST", "/api/v1/ecosystem/security/advisories",
     {"advisory_ref": "CVE-X", "title": "t", "severity": "high", "affected_ref": "y"}),
    ("POST", "/api/v1/ecosystem/benchmark/suites",
     {"key": "kx", "name": "n", "family": "image_generation", "capability_key": "c"}),
]


@pytest.fixture
async def http():
    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as c:
        yield c
    app.router.lifespan_context = orig


@pytest.fixture
async def tokens():
    """A committed member + admin token pair (visible to request sessions)."""
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        member = await _mk_user(db)
        admin = await _mk_user(db, "admin")
        await db.commit()
        yield {
            "member": create_access_token(member.id, member.email, member.role.value),
            "admin": create_access_token(admin.id, admin.email, admin.role.value),
        }
    await engine.dispose()


async def test_anonymous_gets_401_everywhere(http):
    for path in MEMBER_READ_PATHS:
        r = await http.get(path)
        assert r.status_code == 401, f"{path} -> {r.status_code}"
        body = r.json()
        assert "error" in body and body["error"]["code"], path
    for method, path, payload in ADMIN_ONLY:
        r = await http.request(method, path, json=payload)
        assert r.status_code == 401, f"{method} {path} -> {r.status_code}"


async def test_member_reads_return_data_envelope(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    for path in MEMBER_READ_PATHS:
        r = await http.get(path, headers=headers)
        assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
        assert "data" in r.json(), path


async def test_member_blocked_from_admin_surfaces(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    for method, path, payload in ADMIN_ONLY:
        r = await http.request(method, path, json=payload, headers=headers)
        assert r.status_code == 403, f"{method} {path} -> {r.status_code}: {r.text[:200]}"


async def test_error_shapes_are_machine_readable(http, tokens):
    headers = {"Authorization": f"Bearer {tokens['member']}"}
    # Unknown catalog kind → uniform 404 with machine code
    r = await http.get("/api/v1/ecosystem/catalog/nonsense-kind", headers=headers)
    assert r.status_code == 404
    assert r.json()["error"]["code"]
    # compare with too few ids → 422 VALIDATION_ERROR
    r = await http.get(
        "/api/v1/ecosystem/compare", params={"kind": "model", "ids": "a"}, headers=headers
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    # Nonexistent entity scorecard → uniform 404, no existence oracle
    r = await http.get(
        f"/api/v1/ecosystem/catalog/models/{'0' * 26}/scorecard", headers=headers
    )
    assert r.status_code == 404

CORE_ENDPOINTS = {
    # (method, path) pairs that MUST exist — removing one is a breaking change.
    ("POST", "/api/v1/ecosystem/sources"),
    ("POST", "/api/v1/ecosystem/sources/{source_id}/sync"),
    ("GET", "/api/v1/ecosystem/observations"),
    ("GET", "/api/v1/ecosystem/changes"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}/{entity_id}/scorecard"),
    ("GET", "/api/v1/ecosystem/catalog/{segment}/duplicates"),
    ("GET", "/api/v1/ecosystem/compare"),
    ("POST", "/api/v1/ecosystem/pricing/estimate"),
    ("GET", "/api/v1/ecosystem/pricing/history"),
    ("GET", "/api/v1/ecosystem/pricing/availability/uptime"),
    ("GET", "/api/v1/ecosystem/benchmark/leaderboard"),
    ("GET", "/api/v1/ecosystem/benchmark/score-history"),
    ("POST", "/api/v1/ecosystem/benchmark/runs/{run_id}/cancel"),
    ("GET", "/api/v1/ecosystem/benchmark/suites/{suite_id}/export"),
    ("POST", "/api/v1/ecosystem/benchmark/suites/import"),
    ("POST", "/api/v1/ecosystem/watchlists/quick-watch"),
    ("PATCH", "/api/v1/ecosystem/watchlists/{watchlist_id}"),
    ("GET", "/api/v1/ecosystem/dashboard"),
    ("GET", "/api/v1/ecosystem/dashboard/coverage"),
    ("GET", "/api/v1/ecosystem/dashboard/trending"),
    ("GET", "/api/v1/ecosystem/export/changes"),
    ("GET", "/api/v1/ecosystem/export/changes.atom"),
    ("GET", "/api/v1/ecosystem/audit"),
    ("GET", "/api/v1/ecosystem/audit.csv"),
    ("GET", "/api/v1/ecosystem/ops/metrics"),
    ("POST", "/api/v1/ecosystem/security/advisories"),
    ("GET", "/api/v1/ecosystem/security/advisories/{advisory_id}/affected"),
    ("GET", "/api/v1/ecosystem/deprecation-calendar.ics"),
}


def test_core_ecosystem_api_surface_is_stable():
    """API-contract bar: the core eco surface may only GROW. A missing pair
    here means a breaking change shipped without a deliberate decision."""
    from app.main import app

    spec = app.openapi()
    present = {
        (method.upper(), path)
        for path, ops in spec["paths"].items()
        if "/ecosystem" in path
        for method in ops
        if method.lower() in ("get", "post", "put", "patch", "delete")
    }
    missing = CORE_ENDPOINTS - present
    assert not missing, f"Breaking API change — endpoints gone: {sorted(missing)}"
