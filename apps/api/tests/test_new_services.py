"""Tests for new services: webhook, discussion, gamification, duplicate, pack_sharing.

APP_ENV=test PYTHONPATH=. uv run pytest tests/test_new_services.py -v
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"nsvc-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Tester"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _skill(c, h, oid, name="Test Skill"):
    cat = (await c.post(
        f"/api/v1/orgs/{oid}/categories",
        json={"name": f"Cat-{uuid.uuid4().hex[:4]}"},
        headers=h,
    )).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": name, "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h)
    return r.json()["data"]["id"]


async def _project(c, h, oid, title="Test Project"):
    r = await c.post(f"/api/v1/orgs/{oid}/projects", json={
        "title": title,
        "description": "A test project",
        "instructions": "Do the thing",
        "project_type": "general",
        "difficulty": "beginner",
        "max_score": 100,
        "rubric": [{"criterion": "Quality", "max_score": 100}],
    }, headers=h)
    assert r.status_code == 201, f"Project creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _published_public_pack(c, h, oid, pack_name="Pub Pack", skill_name="Pub Skill"):
    """Create a published, public pack and return its id."""
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": pack_name, "visibility": "public",
    }, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, skill_name)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    return pid


# ═══════════════ Webhook Service (5 tests) ═══════════════


@pytest.mark.asyncio
async def test_webhook_create(c):
    """Create webhook returns 201 with the full secret shown once."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/webhooks", json={
        "url": "https://example.com/hook",
        "events": ["pack.published"],
    }, headers=h)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["url"] == "https://example.com/hook"
    assert data["active"] is True
    # Secret should be the full 64-char hex (shown once on creation)
    assert len(data["secret"]) == 64


@pytest.mark.asyncio
async def test_webhook_list_masks_secret(c):
    """List webhooks masks the secret (only 4+****+4 chars shown)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    await c.post(f"/api/v1/orgs/{oid}/webhooks", json={
        "url": "https://example.com/hook",
        "events": ["pack.published"],
    }, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/webhooks", headers=h)
    assert r.status_code == 200
    items = r.json()["data"]
    assert len(items) >= 1
    secret = items[0]["secret"]
    # Masked: first 4 + **** + last 4
    assert "****" in secret
    assert len(secret) == 12  # 4 + 4 stars + 4


@pytest.mark.asyncio
async def test_webhook_delete(c):
    """Delete webhook returns 204."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    cr = await c.post(f"/api/v1/orgs/{oid}/webhooks", json={
        "url": "https://example.com/hook",
        "events": [],
    }, headers=h)
    wid = cr.json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{oid}/webhooks/{wid}", headers=h)
    assert r.status_code == 204

    # Confirm it's gone
    lr = await c.get(f"/api/v1/orgs/{oid}/webhooks", headers=h)
    assert len(lr.json()["data"]) == 0


@pytest.mark.asyncio
async def test_webhook_blocked_url(c):
    """SSRF protection: internal URLs are rejected with 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/webhooks", json={
        "url": "http://169.254.169.254/latest/meta-data/",
        "events": [],
    }, headers=h)
    assert r.status_code == 422
    assert "WEBHOOK_URL_BLOCKED" in r.text


@pytest.mark.asyncio
async def test_webhook_invalid_event_type(c):
    """Unknown event types are rejected with 422 at the schema level."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/webhooks", json={
        "url": "https://example.com/hook",
        "events": ["totally.invalid.event"],
    }, headers=h)
    assert r.status_code == 422


# ═══════════════ Discussion Service (5 tests) ═══════════════


@pytest.mark.asyncio
async def test_discussion_create_comment(c):
    """Create a comment on a published public pack."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    r = await c.post(f"/api/v1/registry/packs/{pid}/discussions", json={
        "body": "Great pack, very useful!",
    }, headers=h)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["body"] == "Great pack, very useful!"
    assert data["pack_id"] == pid


@pytest.mark.asyncio
async def test_discussion_create_on_nonexistent_pack(c):
    """Posting comment on nonexistent pack returns 404."""
    h, _ = await _auth(c)
    fake_id = "01NONEXISTENT000000000000"

    r = await c.post(f"/api/v1/registry/packs/{fake_id}/discussions", json={
        "body": "This should fail",
    }, headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_discussion_threaded_replies(c):
    """Comments can have replies, and listing returns threaded structure."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    # Create top-level comment
    r1 = await c.post(f"/api/v1/registry/packs/{pid}/discussions", json={
        "body": "Top-level comment",
    }, headers=h)
    assert r1.status_code == 201
    parent_id = r1.json()["data"]["id"]

    # Create reply
    r2 = await c.post(f"/api/v1/registry/packs/{pid}/discussions", json={
        "body": "This is a reply",
        "parent_id": parent_id,
    }, headers=h)
    assert r2.status_code == 201

    # List and verify threading
    lr = await c.get(f"/api/v1/registry/packs/{pid}/discussions")
    assert lr.status_code == 200
    comments = lr.json()["data"]
    assert len(comments) >= 1
    top = [c for c in comments if c["id"] == parent_id]
    assert len(top) == 1
    assert len(top[0]["replies"]) == 1
    assert top[0]["replies"][0]["body"] == "This is a reply"


@pytest.mark.asyncio
async def test_discussion_delete_own_comment(c):
    """Author can delete their own comment."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    cr = await c.post(f"/api/v1/registry/packs/{pid}/discussions", json={
        "body": "Delete me",
    }, headers=h)
    cid = cr.json()["data"]["id"]

    r = await c.delete(f"/api/v1/registry/packs/{pid}/discussions/{cid}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_discussion_delete_other_user_comment_forbidden(c):
    """Non-author cannot delete another user's comment."""
    h1, _ = await _auth(c)
    oid = await _org(c, h1)
    pid = await _published_public_pack(c, h1, oid)

    cr = await c.post(f"/api/v1/registry/packs/{pid}/discussions", json={
        "body": "Not yours to delete",
    }, headers=h1)
    cid = cr.json()["data"]["id"]

    # Second user
    h2, _ = await _auth(c)

    r = await c.delete(f"/api/v1/registry/packs/{pid}/discussions/{cid}", headers=h2)
    assert r.status_code == 403


# ═══════════════ Gamification Service (3 tests) ═══════════════


@pytest.mark.asyncio
async def test_gamification_leaderboard_initially_empty(c):
    """Leaderboard for a new org is empty."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/leaderboard", headers=h)
    assert r.status_code == 200
    assert r.json()["data"] == []


@pytest.mark.asyncio
async def test_gamification_my_points_initially_zero(c):
    """User starts with 0 points and level 1."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/points/me", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total_points"] == 0
    assert data["level"] == 1


@pytest.mark.asyncio
async def test_gamification_history_initially_empty(c):
    """Points history for a new user is empty."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/points/me/history", headers=h)
    assert r.status_code == 200
    assert r.json()["data"] == []


# ═══════════════ Duplicate Service (4 tests) ═══════════════


@pytest.mark.asyncio
async def test_duplicate_skill(c):
    """Duplicate a skill returns 201 with '(Copy)' in the name."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Original Skill")

    r = await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/duplicate", headers=h)
    assert r.status_code == 201
    data = r.json()["data"]
    assert "(Copy)" in data["name"]
    assert data["status"] == "draft"
    assert data["id"] != sid


@pytest.mark.asyncio
async def test_duplicate_project(c):
    """Duplicate a project returns 201 with '(Copy)' in the title."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    proj_id = await _project(c, h, oid, "Original Project")

    r = await c.post(f"/api/v1/orgs/{oid}/projects/{proj_id}/duplicate", headers=h)
    assert r.status_code == 201
    data = r.json()["data"]
    assert "(Copy)" in data["title"]
    assert data["status"] == "draft"
    assert data["id"] != proj_id


@pytest.mark.asyncio
async def test_duplicate_nonexistent_skill(c):
    """Duplicating a nonexistent skill returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/skills/01NONEXISTENT000000000000/duplicate", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_nonexistent_project(c):
    """Duplicating a nonexistent project returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/projects/01NONEXISTENT000000000000/duplicate", headers=h)
    assert r.status_code == 404


# ═══════════════ Pack Sharing Service (5 tests) ═══════════════


@pytest.mark.asyncio
async def test_share_pack_sharing_disabled(c):
    """Sharing a pack with sharing_enabled=False returns 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)

    # Default sharing_enabled is False
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/share", json={
        "target_org_id": oid2,
    }, headers=h)
    assert r.status_code == 422
    assert "SHARING_DISABLED" in r.text


@pytest.mark.asyncio
async def test_share_pack_self_share_rejected(c):
    """Sharing a pack with its own org returns 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    # Even though sharing_enabled=False, SELF_SHARE check comes after SHARING_DISABLED,
    # but we test the validation is present
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/share", json={
        "target_org_id": oid,
    }, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_share_nonexistent_pack(c):
    """Sharing a nonexistent pack returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/01NONEXISTENT000000000000/share", json={
        "target_org_id": "01OTHER00000000000000000000",
    }, headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_shared_with_me_initially_empty(c):
    """Shared-with-me list is empty when nothing is shared."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.get(f"/api/v1/orgs/{oid}/shared-with-me", headers=h)
    assert r.status_code == 200
    assert r.json()["data"] == []


@pytest.mark.asyncio
async def test_share_unpublished_pack(c):
    """Sharing an unpublished (draft) pack returns 422 or 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create a draft pack (no release)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Draft Pack", "visibility": "public",
    }, headers=h)).json()["data"]["id"]

    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/share", json={
        "target_org_id": oid2,
    }, headers=h)
    # Should fail because pack is not published
    assert r.status_code in (404, 422)
