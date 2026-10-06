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


@pytest.mark.asyncio
async def test_identity_links_listing_is_own_rows_only(c):
    """§4.17 transparency (round 261): each caller sees exactly THEIR
    linked anonymous ids, newest first; another user's listing never leaks
    them; unauthenticated is 401."""
    h1, u1 = await _auth(c, "Lister")
    h2, _u2 = await _auth(c, "Other")

    a1, a2 = _anon_id(), _anon_id()
    for anon in (a1, a2):
        r = await c.post("/api/v1/experiments/self/identity-link",
                         headers=h1, json={"anonymous_id": anon})
        assert r.status_code == 200

    r = await c.get("/api/v1/experiments/self/identity-links", headers=h1)
    assert r.status_code == 200
    mine = [row["anonymous_id"] for row in r.json()["data"]]
    assert set(mine) >= {a1, a2}
    assert mine.index(a2) < mine.index(a1)  # newest first

    r = await c.get("/api/v1/experiments/self/identity-links", headers=h2)
    assert r.status_code == 200
    theirs = {row["anonymous_id"] for row in r.json()["data"]}
    assert not ({a1, a2} & theirs)  # never another user's links

    r = await c.get("/api/v1/experiments/self/identity-links")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_self_exposure_status_code_pin(c):
    """Wave-45 killer: the self exposure endpoint answers 201 (created-ish
    append semantics) even for the fail-safe recorded=false shape."""
    h, _u = await _auth(c, "ExpPin")
    r = await c.post("/api/v1/experiments/self/exposures", headers=h,
                     json={"experiment_key": "idapi-no-such-exp",
                           "dedup_key": "idapi-pin"})
    assert r.status_code == 201
    assert r.json()["data"]["recorded"] is False


@pytest.mark.asyncio
async def test_identity_links_listing_caps_at_hundred(c):
    """Round 267 (accumulation-bomb law): 101 links list as the newest
    100 — the oldest drops; the deterministic tiebreak keeps
    same-timestamp rows stable."""
    h, _u = await _auth(c, "Capped")
    ids = [_anon_id() for _ in range(101)]
    for anon in ids:
        r = await c.post("/api/v1/experiments/self/identity-link",
                         headers=h, json={"anonymous_id": anon})
        assert r.status_code == 200
    r = await c.get("/api/v1/experiments/self/identity-links", headers=h)
    assert r.status_code == 200
    listed = [row["anonymous_id"] for row in r.json()["data"]]
    assert len(listed) == 100
    assert set(listed) <= set(ids)


@pytest.mark.asyncio
async def test_formula_shaped_anonymous_ids_are_422(c):
    """#83 (round 301): the colon-only wall let Excel formula payloads
    ("=1+2", "+cmd", "@SUM(1)", "-2+3") become unit_id and ride the
    assignments CSV export. The write boundary pins [A-Za-z0-9_-]."""
    payloads = ["=1+2", "+cmd|calc", "@SUM(A1)", "-2+3", "a b", "a:b"]
    for bad in payloads:
        r = await c.post("/api/v1/experiments/anon/resolve",
                         json={"experiment_key": "any", "anonymous_id": bad})
        assert r.status_code == 422, (bad, r.status_code, r.text[:200])
        r = await c.post("/api/v1/experiments/anon/exposures",
                         json={"experiment_key": "any", "anonymous_id": bad})
        assert r.status_code == 422, (bad, r.status_code)
    h, _u = await _auth(c, "CsvWall")
    r = await c.post("/api/v1/experiments/self/identity-link",
                     headers=h, json={"anonymous_id": "=HYPERLINK(1)"})
    assert r.status_code == 422
    # the SDK's Crockford shape still passes the wall (resolve may 404 the
    # unknown experiment or fail-safe — anything but a validation error)
    r = await c.post("/api/v1/experiments/anon/resolve",
                     json={"experiment_key": "any",
                           "anonymous_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV"})
    assert r.status_code != 422


@pytest.mark.asyncio
async def test_timeline_note_wall_and_boundary(c):
    """Round 318: a plain user hits the #59 wall (403 BEFORE validation);
    the text boundary (#87 class: ctrl chars, oversize) is pinned on the
    schema directly."""
    import pydantic

    from app.experiments.schemas import ExperimentNoteRequest

    h, _u = await _auth(c, "Noter")
    r = await c.post(f"/api/v1/experiments/{'x' * 26}/notes",
                     headers=h, json={"text": "hello"})
    assert r.status_code == 403  # read-scope wall holds for writes too
    with pytest.raises(pydantic.ValidationError):
        ExperimentNoteRequest(text="bad\x00ctrl")
    with pytest.raises(pydantic.ValidationError):
        ExperimentNoteRequest(text="y" * 501)
    assert ExperimentNoteRequest(text="  ok note  ").text == "ok note"
