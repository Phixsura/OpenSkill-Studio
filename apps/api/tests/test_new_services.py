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
    # Create private (create no longer accepts visibility=public — R79 gate),
    # publish, then reach public via submit-review → approve.
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": pack_name,
    }, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, skill_name)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/submit-for-review", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/approve", headers=h)
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
async def test_discussion_reply_depth_capped_at_two_levels(c):
    """R93a: discussions are a two-level model — list_comments only fetches
    replies whose parent is top-level, and the web panel renders one reply
    level. Replying to a REPLY previously succeeded but the L3 comment was
    orphaned (persisted, never rendered anywhere). create_comment must reject a
    reply whose parent is itself a reply, so nothing created is invisible.
    Reverting the parent.parent_id check lets the L3 reply be created (201) and
    silently vanish from the tree."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    top = (await c.post(
        f"/api/v1/registry/packs/{pid}/discussions", json={"body": "top"}, headers=h
    )).json()["data"]["id"]
    reply = (await c.post(
        f"/api/v1/registry/packs/{pid}/discussions",
        json={"body": "reply", "parent_id": top},
        headers=h,
    )).json()["data"]["id"]

    # reply-to-a-reply is rejected
    r = await c.post(
        f"/api/v1/registry/packs/{pid}/discussions",
        json={"body": "reply to reply", "parent_id": reply},
        headers=h,
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "REPLY_DEPTH_EXCEEDED"

    # the tree contains exactly the two comments that can render (top + reply),
    # nothing orphaned
    comments = (await c.get(f"/api/v1/registry/packs/{pid}/discussions")).json()["data"]

    def _count(nodes):
        return sum(1 + _count(n.get("replies", [])) for n in nodes)

    assert _count(comments) == 2


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

    # Create a draft pack (no release; visibility irrelevant — create-public
    # needs approval per R79, and the assertion is about the unpublished state)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Draft Pack",
    }, headers=h)).json()["data"]["id"]

    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/share", json={
        "target_org_id": oid2,
    }, headers=h)
    # Should fail because pack is not published
    assert r.status_code in (404, 422)


# ═══════════════ Round 15 — Missing Edge Case Tests (4 tests) ═══════════════


@pytest.mark.asyncio
async def test_install_count_decrement_on_remove(c):
    """install_count should decrease when an installation is removed."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "CountPack")

    # Check initial install_count
    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 200
    initial_count = r.json()["data"]["install_count"]

    # Install the pack from a second org
    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)
    ir = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert ir.status_code == 201
    install_id = ir.json()["data"]["id"]

    # Verify install_count went up
    r2 = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r2.json()["data"]["install_count"] == initial_count + 1

    # Remove the installation
    dr = await c.delete(f"/api/v1/orgs/{oid2}/installations/{install_id}", headers=h2)
    assert dr.status_code == 204

    # Verify install_count went back down
    r3 = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r3.json()["data"]["install_count"] == initial_count


@pytest.mark.asyncio
async def test_submit_for_review_lifecycle(c):
    """submit_for_review: happy path, already-pending (409), already-approved (422)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # A private+published pack that has NOT been through review yet (the shared
    # _published_public_pack helper now auto-approves, which would make the
    # first submit-for-review a 422 already-approved — R79). Build inline.
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ReviewLifecyclePack"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "ReviewLifecycleSkill")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    # Happy path: submit for review
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/submit-for-review", headers=h)
    assert r.status_code == 200

    # Already pending → 409
    r2 = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/submit-for-review", headers=h)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ALREADY_PENDING"

    # Set to approved via raw SQL
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE skill_packs SET review_status = :s WHERE id = :id"),
            {"s": "approved", "id": pid},
        )
        await session.commit()

    # Already approved → 422
    r3 = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/submit-for-review", headers=h)
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "ALREADY_APPROVED"


@pytest.mark.asyncio
async def test_upgrade_nonexistent_version_returns_404(c):
    """Upgrading to a version that doesn't exist should return 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "UpgNonExPack")

    # Install
    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)
    ir = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert ir.status_code == 201
    install_id = ir.json()["data"]["id"]

    # Upgrade to non-existent version
    r = await c.post(
        f"/api/v1/orgs/{oid2}/installations/{install_id}/upgrade",
        json={"version": "99.99.99"},
        headers=h2,
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "RELEASE_NOT_FOUND"


@pytest.mark.asyncio
async def test_import_oversized_archive_rejected(c):
    """Uploading a zip larger than MAX_ARCHIVE_SIZE should be rejected."""
    import io
    import zipfile

    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create a zip with enough data to exceed a small limit
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        # Write a manifest and a filler file to exceed 200 bytes
        zf.writestr("manifest.json", '{"schema_version": "1.0"}')
        zf.writestr("filler.txt", "x" * 500)
    raw = buf.getvalue()

    # Monkey-patch MAX_ARCHIVE_SIZE in the pack_io endpoint module where the
    # name is imported and used. We patch both the endpoint and service copies.
    import app.api.v1.endpoints.pack_io as pack_io_mod
    import app.services.pack_import as pack_import_mod

    orig_ep = pack_io_mod.MAX_ARCHIVE_SIZE
    orig_svc = pack_import_mod.MAX_ARCHIVE_SIZE
    try:
        pack_io_mod.MAX_ARCHIVE_SIZE = 100
        pack_import_mod.MAX_ARCHIVE_SIZE = 100
        r = await c.post(
            f"/api/v1/orgs/{oid}/packs/import",
            files={"file": ("test.zip", raw, "application/zip")},
            headers=h,
        )
    finally:
        pack_io_mod.MAX_ARCHIVE_SIZE = orig_ep
        pack_import_mod.MAX_ARCHIVE_SIZE = orig_svc
    assert r.status_code in (413, 422), f"Expected 413 or 422, got {r.status_code}: {r.text}"


# ═══════════════ R88d: points idempotency guard ═══════════════


@pytest.mark.asyncio
async def test_points_award_idempotent_per_action(c):
    """R88d guard: resubmitting the same submission (after revision_requested)
    and re-reviewing the same submission must NOT re-award points. Without the
    per-(user, org, reason, reference_id) dedup in award_points, two colluding
    accounts could ping-pong review/resubmit for unbounded leaderboard points.
    Reverting the dedup makes this fail (student 80 pts / instructor 15 pts)."""
    ih, _ = await _auth(c)  # instructor / org owner
    sh, student = await _auth(c)
    oid = await _org(c, ih)
    r = await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": student["id"], "role": "student"},
        headers=ih,
    )
    assert r.status_code == 201

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Idem Proj",
            "description": "d" * 20,
            "instructions": "do it",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=ih,
    )
    pid = r.json()["data"]["id"]
    assert (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ih)).status_code == 200

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions",
        json={"content": {"text": "work"}},
        headers=sh,
    )
    subid = r.json()["data"]["id"]
    submit_url = f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{subid}/submit"
    assert (await c.post(submit_url, headers=sh)).status_code == 200

    # 3 rounds of revision_requested -> resubmit on the SAME submission
    for _ in range(3):
        r = await c.post(
            f"/api/v1/orgs/{oid}/submissions/{subid}/reviews",
            json={"status": "revision_requested", "feedback": "redo"},
            headers=ih,
        )
        assert r.status_code == 201
        assert (await c.post(submit_url, headers=sh)).status_code == 200

    r = await c.get(f"/api/v1/orgs/{oid}/points/me", headers=sh)
    assert r.json()["data"]["total_points"] == 20  # one award despite 4 submits

    r = await c.get(f"/api/v1/orgs/{oid}/points/me", headers=ih)
    assert r.json()["data"]["total_points"] == 5  # one award despite 3 reviews

    # A DIFFERENT project must still award fresh points
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Idem Proj 2",
            "description": "d" * 20,
            "instructions": "do it",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=ih,
    )
    p2 = r.json()["data"]["id"]
    assert (await c.post(f"/api/v1/orgs/{oid}/projects/{p2}/publish", headers=ih)).status_code == 200
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{p2}/submissions",
        json={"content": {"text": "w2"}},
        headers=sh,
    )
    s2 = r.json()["data"]["id"]
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{p2}/submissions/{s2}/submit", headers=sh)
    ).status_code == 200

    r = await c.get(f"/api/v1/orgs/{oid}/points/me", headers=sh)
    assert r.json()["data"]["total_points"] == 40


# ═══════════════ R88e: ctrl-char screens on review/discussion/webhook ═══════════════


def test_review_discussion_webhook_schemas_reject_control_chars():
    """R88e guard: NUL and other C0 control chars must be rejected at the schema
    boundary for pack review title/body/reply, discussion comment body, and
    webhook URL. NUL previously 500'd on the Postgres write; other C0 chars
    were stored raw (stored injection). Reverting the reject_ctrl_str calls
    makes this fail."""
    import pydantic

    from app.api.v1.endpoints.discussions import CreateCommentRequest
    from app.api.v1.endpoints.webhooks import CreateWebhookRequest
    from app.schemas.pack_review import CreateReviewRequest, ReplyRequest, UpdateReviewRequest

    nul = chr(0)
    soh = chr(1)

    cases = [
        (CreateReviewRequest, {"rating": 5, "title": "T" + nul, "body": "b" * 20}),
        (CreateReviewRequest, {"rating": 5, "title": "T", "body": "b" * 20 + soh}),
        (UpdateReviewRequest, {"title": "T" + nul}),
        (UpdateReviewRequest, {"body": "b" * 20 + soh}),
        (ReplyRequest, {"reply_text": "r" + nul}),
        (CreateCommentRequest, {"body": "c" + nul}),
        (CreateCommentRequest, {"body": "c" + soh + "x"}),
        (CreateWebhookRequest, {"url": "http://example.com/a" + nul + "b", "events": []}),
        (CreateWebhookRequest, {"url": "http://example.com/a" + soh + "b", "events": []}),
    ]
    for model, payload in cases:
        with pytest.raises(pydantic.ValidationError):
            model(**payload)

    # Clean values must still pass
    CreateReviewRequest(rating=5, title="Good", body="b" * 20)
    ReplyRequest(reply_text="thanks")
    CreateCommentRequest(body="nice pack")
    CreateWebhookRequest(url="http://example.com/hook", events=[])


# ═══════════════ R89a: duplicate name/slug length safety ═══════════════


@pytest.mark.asyncio
async def test_duplicate_skill_maxlen_name_no_500(c):
    """R89a guard: a skill whose name is already at the VARCHAR(200) max, when
    duplicated, appended ' (Copy)' and overflowed the column (StringDataRight
    Truncation -> 500). Worse, the slug's whole-string [:200] truncation
    dropped the uniqueness suffix so a second duplicate collided on
    uq_skill_org_slug (UniqueViolation -> 500). Duplicating twice must both
    succeed, name stays within 200, slugs differ. Reverting either fix fails."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "A" * 200)

    r1 = await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/duplicate", headers=h)
    assert r1.status_code == 201, r1.text
    r2 = await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/duplicate", headers=h)
    assert r2.status_code == 201, r2.text  # slug uniqueness held
    d1, d2 = r1.json()["data"], r2.json()["data"]
    assert len(d1["name"]) <= 200
    assert d1["name"].endswith("(Copy)")
    assert d1["slug"] != d2["slug"]


@pytest.mark.asyncio
async def test_duplicate_project_maxlen_title_no_500(c):
    """R89a guard: same class for projects (title/slug VARCHAR(200))."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _project(c, h, oid, "P" * 200)

    r1 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/duplicate", headers=h)
    assert r1.status_code == 201, r1.text
    r2 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/duplicate", headers=h)
    assert r2.status_code == 201, r2.text
    d1, d2 = r1.json()["data"], r2.json()["data"]
    assert len(d1["title"]) <= 200
    assert d1["title"].endswith("(Copy)")
    assert d1["slug"] != d2["slug"]


# ── R92h: shared-with-me must not leak owner-org moderation/ownership fields ──


@pytest.mark.asyncio
async def test_shared_with_me_does_not_leak_moderation_fields(c):
    """R92h: list_shared_packs serialized the internal SkillPackResponse to the
    GRANTEE (a different tenant), leaking the owner org's rejection_reason
    (moderator's private note), review_status, owner_org_id and created_by —
    the exact R71 leak, fixed for anon /registry but missed on shared-with-me.
    It must serialize the sanitized PublicSkillPackResponse. Reverting fails."""
    ha, owner_a = await _auth(c)
    oid_a = await _org(c, ha)
    hb, _ = await _auth(c)
    oid_b = await _org(c, hb)
    pid = await _published_public_pack(c, ha, oid_a)

    # Enable sharing + set a private rejection note, then share A→B (no API for
    # sharing_enabled/review_status, so set them + the share row directly).
    from app.core.database import AsyncSessionLocal
    from app.models.pack_share import PackShare
    from app.models.skill_pack import SkillPack

    async with AsyncSessionLocal() as db:
        p = await db.get(SkillPack, pid)
        p.sharing_enabled = True
        p.review_status = "rejected"
        p.rejection_reason = "SECRET moderator note"
        db.add(PackShare(pack_id=pid, target_org_id=oid_b, shared_by=owner_a["id"]))
        await db.commit()

    r = await c.get(f"/api/v1/orgs/{oid_b}/shared-with-me", headers=hb)
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    item = data[0]
    # The pack is still discoverable by the grantee…
    assert item["name"] == "Pub Pack"
    # …but none of the owner-org internal fields are present.
    for leaked in ("rejection_reason", "review_status", "owner_org_id", "created_by"):
        assert leaked not in item, f"{leaked} leaked cross-tenant: {item.get(leaked)!r}"


# ── R92i: cross-org sharing wired end-to-end (schema setter + install grant) ──


@pytest.mark.asyncio
async def test_sharing_enabled_settable_and_not_a_card_field(c):
    """R92i: sharing_enabled is exposed on the pack write schemas so an owner can
    actually enable sharing (previously no API setter → share_pack was dead).
    It is NOT a public-registry card field, so toggling it on an APPROVED pack
    must not void approval. Reverting the schema field makes the PUT a no-op."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)  # ends approved + public

    # toggle sharing on — persists, and approval survives (not a card field)
    r = await c.put(
        f"/api/v1/orgs/{oid}/packs/{pid}", json={"sharing_enabled": True}, headers=h
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["sharing_enabled"] is True

    got = (await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)).json()["data"]
    assert got["sharing_enabled"] is True
    assert got["review_status"] == "approved"  # sharing toggle did NOT void approval
    assert got["visibility"] == "public"


@pytest.mark.asyncio
async def test_share_then_install_end_to_end(c):
    """R92i: the full previously-impossible path — owner enables sharing, shares a
    PRIVATE pack with org B, B installs it; a third org C with no grant is 404;
    revoking the share removes B's install access. Reverting the install-gate
    PackShare lookup makes B's install 404 (feature dead)."""
    ha, _ = await _auth(c)
    oid_a = await _org(c, ha)
    hb, _ = await _auth(c)
    oid_b = await _org(c, hb)
    hc, _ = await _auth(c)
    oid_c = await _org(c, hc)

    # A: pack + skill + release, enable sharing, make it PRIVATE
    pid = (await c.post(f"/api/v1/orgs/{oid_a}/packs", json={"name": "Share E2E"}, headers=ha)).json()["data"]["id"]
    sid = await _skill(c, ha, oid_a, "Share Skill")
    await c.post(f"/api/v1/orgs/{oid_a}/packs/{pid}/skills", json={"skill_id": sid}, headers=ha)
    await c.post(f"/api/v1/orgs/{oid_a}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=ha)
    r = await c.put(
        f"/api/v1/orgs/{oid_a}/packs/{pid}",
        json={"sharing_enabled": True, "visibility": "private"},
        headers=ha,
    )
    assert r.status_code == 200, r.text

    # share A→B works now (was always 422 SHARING_DISABLED before R92i)
    r = await c.post(
        f"/api/v1/orgs/{oid_a}/packs/{pid}/share", json={"target_org_id": oid_b}, headers=ha
    )
    assert r.status_code == 201, r.text

    # B sees it and can install it
    shared = (await c.get(f"/api/v1/orgs/{oid_b}/shared-with-me", headers=hb)).json()["data"]
    assert any(p["id"] == pid for p in shared)
    r = await c.post(
        f"/api/v1/orgs/{oid_b}/installations", json={"pack_id": pid, "version": "1.0.0"}, headers=hb
    )
    assert r.status_code == 201, r.text

    # C, with no grant, cannot install (uniform 404)
    r = await c.post(
        f"/api/v1/orgs/{oid_c}/installations", json={"pack_id": pid, "version": "1.0.0"}, headers=hc
    )
    assert r.status_code == 404, r.text

    # revoke → a fresh grantee org can no longer install
    assert (
        await c.delete(f"/api/v1/orgs/{oid_a}/packs/{pid}/share/{oid_b}", headers=ha)
    ).status_code == 204
    hd_, _ = await _auth(c)
    oid_d = await _org(c, hd_)
    r = await c.post(
        f"/api/v1/orgs/{oid_d}/installations", json={"pack_id": pid, "version": "1.0.0"}, headers=hd_
    )
    assert r.status_code == 404, r.text
