"""Coverage tests for new endpoints and utilities with low coverage.

Targets: client_briefs endpoints (open/withdraw), media_eval, video_eval.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"cov-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Cov"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"Cov-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


# ═══════════════ /briefs/open endpoint ═══════════════


@pytest.mark.asyncio
async def test_briefs_open_endpoint_returns_open_briefs(c):
    """GET /briefs/open returns briefs with status=open."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create brief and set to open
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Open Brief", "client_name": "C", "project_type": "p",
        "objective": "An open brief for coverage testing",
    }, headers=h)).json()["data"]["id"]

    await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "open"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/briefs/open", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) >= 1
    assert any(b["id"] == bid for b in data)
    assert all(b["status"] in ("open", "active") for b in data)


@pytest.mark.asyncio
async def test_briefs_open_endpoint_excludes_draft(c):
    """Draft briefs should not appear in /briefs/open."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create draft brief (don't change status)
    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Draft Brief", "client_name": "C", "project_type": "p",
        "objective": "A draft brief that should not appear",
    }, headers=h)).json()["data"]["id"]

    r = await c.get(f"/api/v1/orgs/{oid}/briefs/open", headers=h)
    assert r.status_code == 200
    assert not any(b["id"] == bid for b in r.json()["data"])


@pytest.mark.asyncio
async def test_briefs_open_endpoint_requires_org_member(c):
    """Non-org-member cannot access /briefs/open."""
    h, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/briefs/open", headers=h2)
    assert r.status_code in (403, 404)


# ═══════════════ /briefs/{id}/withdraw endpoint ═══════════════


@pytest.mark.asyncio
async def test_withdraw_application(c):
    """Learner can withdraw their pending application."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi)

    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Withdraw Brief", "client_name": "C", "project_type": "p",
        "objective": "A brief for testing withdrawal",
    }, headers=hi)).json()["data"]["id"]

    # Apply
    await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/apply", json={"note": "hi"}, headers=hs)

    # Withdraw
    r = await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/withdraw", headers=hs)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "withdrawn"


@pytest.mark.asyncio
async def test_withdraw_no_application(c):
    """Withdrawing without applying returns 404."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi)

    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "No App Brief", "client_name": "C", "project_type": "p",
        "objective": "A brief where nobody applied",
    }, headers=hi)).json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/withdraw", headers=hs)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_withdraw_accepted_application_rejected(c):
    """Cannot withdraw an already-accepted application."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi)

    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Accepted Brief", "client_name": "C", "project_type": "p",
        "objective": "A brief where application was accepted",
    }, headers=hi)).json()["data"]["id"]

    app_r = await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/apply", json={"note": "hi"}, headers=hs)
    app_id = app_r.json()["data"]["id"]

    # Accept the application
    await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}/applications/{app_id}",
                json={"status": "accepted"}, headers=hi)

    # Try to withdraw → should fail
    r = await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/withdraw", headers=hs)
    assert r.status_code == 422


# ═══════════════ media_eval.py ═══════════════


def test_build_image_block():
    """build_image_block creates correct Anthropic content block."""
    from app.core.media_eval import build_image_block

    block = build_image_block("base64data==", "image/png")
    assert block["type"] == "image"
    assert block["source"]["type"] == "base64"
    assert block["source"]["data"] == "base64data=="
    assert block["source"]["media_type"] == "image/png"


def test_fetch_image_function_exists():
    """fetch_image_as_base64 is importable."""
    from app.core.media_eval import fetch_image_as_base64

    assert callable(fetch_image_as_base64)


def test_image_mimes_set():
    """IMAGE_MIMES set contains expected types."""
    from app.core.media_eval import IMAGE_MIMES

    assert "image/png" in IMAGE_MIMES
    assert "image/jpeg" in IMAGE_MIMES
    assert "image/webp" in IMAGE_MIMES


# ═══════════════ video_eval.py ═══════════════


def test_video_eval_check_ffmpeg():
    """check_ffmpeg exists and is callable."""
    from app.core.video_eval import check_ffmpeg

    assert callable(check_ffmpeg)


def test_video_eval_sample_frames_importable():
    """sample_frames function is importable."""
    from app.core.video_eval import sample_frames

    assert callable(sample_frames)


def test_video_eval_frames_to_base64():
    """frames_to_base64 converts frame file paths to base64."""
    import os
    import tempfile

    from app.core.video_eval import frames_to_base64

    # Create a tiny temp image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        # Minimal 1x1 PNG
        f.write(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
            b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
            b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        path = f.name

    try:
        result = frames_to_base64([(path, 1.5)])
        assert len(result) == 1
        b64, media_type, timestamp = result[0]
        assert len(b64) > 0
        assert timestamp == 1.5
    finally:
        os.unlink(path)


def test_video_eval_fetch_and_sample_importable():
    """fetch_video_and_sample is importable."""
    from app.core.video_eval import fetch_video_and_sample

    assert callable(fetch_video_and_sample)


# ═══════════════ Brief status lifecycle ═══════════════


@pytest.mark.asyncio
async def test_brief_status_transitions(c):
    """Brief can transition through lifecycle states."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Lifecycle", "client_name": "C", "project_type": "p",
        "objective": "Testing full brief lifecycle",
    }, headers=h)).json()["data"]["id"]

    # draft → open
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "open"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "open"

    # open → assigned
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "assigned"}, headers=h)
    assert r.status_code == 200

    # assigned → in_production
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "in_production"}, headers=h)
    assert r.status_code == 200

    # in_production → review
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "review"}, headers=h)
    assert r.status_code == 200

    # review → completed
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "completed"}, headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_brief_cancel(c):
    """Brief can be cancelled."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    bid = (await c.post(f"/api/v1/orgs/{oid}/briefs", json={
        "title": "Cancellable", "client_name": "C", "project_type": "p",
        "objective": "A brief that will be cancelled",
    }, headers=h)).json()["data"]["id"]

    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "cancelled"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "cancelled"
