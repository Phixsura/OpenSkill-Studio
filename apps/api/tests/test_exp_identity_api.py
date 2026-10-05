"""§4.17 identity endpoints at the ASGI level (round 257).

The live wall covers these over uvicorn, but the CERT SUITES never
exercised the endpoint layer (the 403 support-override branch in
particular) — this file puts the anon/link surfaces in every full run.
"""

import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"idapi-{uuid.uuid4().hex[:16]}@test.com"


def _anon_id():
    return f"IDAPI{uuid.uuid4().hex[:21].upper()}"[:26]


@pytest_asyncio.fixture
async def c():
    from app.core.database import engine
    from app.main import app

    orig = app.router.lifespan_context

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _auth(c, name="IdApi"):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!",
              "display_name": name},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


@pytest.mark.asyncio
async def test_identity_link_endpoint_contract(c):
    """Claim-own 200 + idempotent; naming another user without platform
    admin is 403 FORBIDDEN; malformed ids 422 at the schema wall; the
    anon surfaces respond without auth (fail-safe shapes)."""
    h1, u1 = await _auth(c, "Owner")
    h2, u2 = await _auth(c, "Intruder")

    anon = _anon_id()
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h1, json={"anonymous_id": anon})
    assert r.status_code == 200
    assert r.json()["data"]["user_id"] == u1["id"]
    # idempotent re-claim
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h1, json={"anonymous_id": anon})
    assert r.status_code == 200

    # rebinding by another identity: typed 422
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h2, json={"anonymous_id": anon})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EXPERIMENT_IDENTITY_CONFLICT"

    # the support override is PLATFORM-ADMIN only (round 232)
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h2,
                     json={"anonymous_id": _anon_id(), "user_id": u1["id"]})
    assert r.status_code == 403

    # schema wall: colon and overlength refuse before any service work
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h1, json={"anonymous_id": "a:b"})
    assert r.status_code == 422
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h1, json={"anonymous_id": "x" * 27})
    assert r.status_code == 422

    # unauthenticated link refused
    r = await c.post("/api/v1/experiments/self/identity-link",
                     json={"anonymous_id": _anon_id()})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_anon_surfaces_fail_safe_without_auth(c):
    """The pre-login surfaces take no auth and fail SAFE: an unknown
    experiment resolves to the default experience (variant null) and an
    exposure for an unassigned unit reports recorded=false — product
    paths never break on experiment plumbing."""
    anon = _anon_id()
    r = await c.post("/api/v1/experiments/anon/resolve",
                     json={"experiment_key": "idapi-no-such-exp",
                           "anonymous_id": anon})
    assert r.status_code == 200
    assert r.json()["data"]["variant_key"] is None
    assert r.json()["data"]["config"] == {}

    r = await c.post("/api/v1/experiments/anon/exposures",
                     json={"experiment_key": "idapi-no-such-exp",
                           "anonymous_id": anon,
                           "dedup_key": "idapi-x"})
    assert r.status_code == 201
    assert r.json()["data"]["recorded"] is False
