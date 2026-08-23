"""Integration tests for skill pack management — CRUD, contents, releases."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"pack-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Pack"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _skill(c, h, oid, name="Test Skill"):
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"Cat-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": name, "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h)
    return r.json()["data"]["id"]


async def _template(c, h, oid, name="Test Template"):
    r = await c.post(f"/api/v1/orgs/{oid}/project-templates", json={
        "name": name, "description": "Template desc", "instructions": "Do the thing",
        "rubric": [{"criterion": "Quality", "max_score": 100}],
    }, headers=h)
    return r.json()["data"]["id"]


# ═══════════════ Pack CRUD ═══════════════


@pytest.mark.asyncio
async def test_create_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "AI Product Photography",
        "summary": "Learn AI product shots",
        "description": "Complete training for AI-powered product photography",
        "visibility": "private",
        "difficulty": "beginner",
        "scenario_tags": ["ecommerce", "product"],
        "learning_outcomes": ["Create hero images", "Control composition"],
    }, headers=h)
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["name"] == "AI Product Photography"
    assert d["slug"].startswith("ai-product-photography")
    assert d["status"] == "draft"
    assert d["visibility"] == "private"
    assert d["install_count"] == 0
    assert len(d["scenario_tags"]) == 2


@pytest.mark.asyncio
async def test_create_pack_duplicate_slug(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Duplicate"}, headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Duplicate"}, headers=h)
    assert r.status_code == 201  # succeeds with modified slug
    assert r.json()["data"]["slug"] != "duplicate"  # slug was deduped


@pytest.mark.asyncio
async def test_list_packs(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Pack A"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Pack B"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_get_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Get Me"}, headers=h)).json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Get Me"


@pytest.mark.asyncio
async def test_update_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Old Name"}, headers=h)).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{oid}/packs/{pid}", json={
        "name": "New Name", "visibility": "public",
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "New Name"
    assert r.json()["data"]["visibility"] == "public"


@pytest.mark.asyncio
async def test_delete_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Delete Me"}, headers=h)).json()["data"]["id"]
    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert r.status_code == 204

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert r.status_code == 404


# ═══════════════ Pack Contents ═══════════════


@pytest.mark.asyncio
async def test_add_skill_to_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Skill Pack"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    assert r.status_code == 201
    assert r.json()["data"]["skill_id"] == sid


@pytest.mark.asyncio
async def test_add_duplicate_skill(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Dup"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_add_cross_org_skill(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "XOrg"}, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h2, oid2)  # skill in other org

    r = await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_remove_skill(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Rm"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}/skills/{sid}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_list_pack_skills(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "List"}, headers=h)).json()["data"]["id"]
    s1 = await _skill(c, h, oid, "Skill A")
    s2 = await _skill(c, h, oid, "Skill B")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": s1, "sort_order": 0}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": s2, "sort_order": 1}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/skills", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["data"][0]["skill_name"] == "Skill A"


@pytest.mark.asyncio
async def test_add_template(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Tmpl"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_add_duplicate_template(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "DupT"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_remove_template(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "RmT"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)

    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}/templates/{tid}", headers=h)
    assert r.status_code == 204


# ═══════════════ Releases ═══════════════


@pytest.mark.asyncio
async def test_publish_release(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Release Pack"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Release Skill")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={
        "version": "1.0.0", "changelog": "Initial release",
    }, headers=h)
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["version"] == "1.0.0"
    assert d["component_count"] >= 1
    assert len(d["checksum"]) == 64  # SHA-256 hex

    # Pack status should be published now
    pr = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert pr.json()["data"]["status"] == "published"


@pytest.mark.asyncio
async def test_publish_empty_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Empty"}, headers=h)).json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EMPTY_PACK"


@pytest.mark.asyncio
async def test_publish_duplicate_version(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "DupV"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_VERSION"


@pytest.mark.asyncio
async def test_publish_invalid_semver(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "BadV"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "v1"}, headers=h)
    assert r.status_code == 422
    # Rejected by Pydantic schema validator (semver format) or service layer
    body = r.json()
    assert "error" in body or "detail" in body


@pytest.mark.asyncio
async def test_release_manifest_contains_skills(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Manifest"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Manifest Skill")
    tid = await _template(c, h, oid, "Manifest Template")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0", headers=h)
    assert r.status_code == 200
    manifest = r.json()["data"]["manifest"]
    assert manifest["schema_version"] == "1"
    assert len(manifest["skills"]) == 1
    assert manifest["skills"][0]["name"] == "Manifest Skill"
    assert len(manifest["project_templates"]) == 1
    assert manifest["project_templates"][0]["name"] == "Manifest Template"


@pytest.mark.asyncio
async def test_release_immutability(c):
    """After publishing, editing source skill doesn't change the release manifest."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Immutable"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Original Name")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    # Edit the source skill
    await c.put(f"/api/v1/orgs/{oid}/skills/{sid}", json={"name": "Changed Name"}, headers=h)

    # Release manifest should still have original name
    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0", headers=h)
    assert r.json()["data"]["manifest"]["skills"][0]["name"] == "Original Name"


@pytest.mark.asyncio
async def test_list_releases(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Multi"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.1.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["data"][0]["version"] == "1.1.0"  # newest first


# ═══════════════ Authorization ═══════════════


@pytest.mark.asyncio
async def test_cross_org_pack_access(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "Private"}, headers=h1)).json()["data"]["id"]

    r = await c.get(f"/api/v1/orgs/{oid2}/packs/{pid}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_student_cannot_create_pack(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Sneaky"}, headers=hs)
    assert r.status_code == 403


# ═══════════════ Extended Coverage ═══════════════


async def _pack_with_skill(c, h, oid, pack_name="Pk", skill_name="Sk"):
    """Create pack + skill inside it, return (pack_id, skill_id)."""
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": pack_name}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, skill_name)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    return pid, sid


async def _category(c, h, oid, name="Cat"):
    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"{name}-{uuid.uuid4().hex[:4]}"}, headers=h)
    return r.json()["data"]["id"]


async def _skill_in_cat(c, h, oid, cat_id, name="Skill"):
    r = await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": name, "description": "d" * 10, "difficulty": "beginner", "category_id": cat_id,
    }, headers=h)
    return r.json()["data"]["id"]


# ── 1. Prerequisite cycle ──


@pytest.mark.asyncio
async def test_publish_release_prerequisite_cycle(c):
    from app.core.database import AsyncSessionLocal
    from app.models.skill import SkillPrerequisite

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "CyclePack"}, headers=h)).json()["data"]["id"]

    sa = await _skill(c, h, oid, "Cycle A")
    sb = await _skill(c, h, oid, "Cycle B")

    # Insert mutual prerequisites directly (the API prevents cycles, so use the model)
    async with AsyncSessionLocal() as session:
        session.add(SkillPrerequisite(skill_id=sa, prerequisite_id=sb))
        session.add(SkillPrerequisite(skill_id=sb, prerequisite_id=sa))
        await session.commit()

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sa}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sb}, headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "PREREQUISITE_CYCLE"


# ── 2. Archived skill ──


@pytest.mark.asyncio
async def test_publish_release_archived_skill(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, sid = await _pack_with_skill(c, h, oid, "ArchPack", "ArchSkill")

    # Archive the skill — this now also removes SkillPackSkill join rows,
    # so the pack becomes empty and publishing fails with EMPTY_PACK
    await c.delete(f"/api/v1/orgs/{oid}/skills/{sid}", headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EMPTY_PACK"


# ── 3. Manifest prerequisites array ──


@pytest.mark.asyncio
async def test_publish_release_manifest_contains_prerequisites(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "PrereqManifest"}, headers=h)).json()["data"]["id"]

    sa = await _skill(c, h, oid, "Prereq Base")
    sb = await _skill(c, h, oid, "Prereq Dependent")

    # B requires A (no cycle, safe via API)
    await c.put(f"/api/v1/orgs/{oid}/skills/{sb}/prerequisites", json={"prerequisite_ids": [sa]}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sa, "sort_order": 0}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sb, "sort_order": 1}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0", headers=h)
    assert r.status_code == 200
    manifest = r.json()["data"]["manifest"]
    skills = manifest["skills"]
    skill_b = next(s for s in skills if s["name"] == "Prereq Dependent")
    assert len(skill_b["prerequisites"]) >= 1
    skill_a = next(s for s in skills if s["name"] == "Prereq Base")
    assert len(skill_a["prerequisites"]) == 0


# ── 4. Deduplicated categories ──


@pytest.mark.asyncio
async def test_publish_release_manifest_deduplicates_categories(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "DedupCat"}, headers=h)).json()["data"]["id"]

    cat_id = await _category(c, h, oid, "SharedCat")
    s1 = await _skill_in_cat(c, h, oid, cat_id, "CatSkill1")
    s2 = await _skill_in_cat(c, h, oid, cat_id, "CatSkill2")

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": s1}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": s2}, headers=h)

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0", headers=h)
    manifest = r.json()["data"]["manifest"]
    assert len(manifest["categories"]) == 1


# ── 5. Already published stays published ──


@pytest.mark.asyncio
async def test_publish_release_already_published_keeps_status(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, _ = await _pack_with_skill(c, h, oid, "AlreadyPub", "PubSk")

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    r1 = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert r1.json()["data"]["status"] == "published"

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h)
    r2 = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    assert r2.json()["data"]["status"] == "published"


# ── 6. Update archived pack ──


@pytest.mark.asyncio
async def test_update_archived_pack_returns_404(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ArchUpd"}, headers=h)).json()["data"]["id"]

    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.put(f"/api/v1/orgs/{oid}/packs/{pid}", json={"name": "Nope"}, headers=h)
    assert r.status_code == 404


# ── 7. Add skill to archived pack ──


@pytest.mark.asyncio
async def test_add_skill_to_archived_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ArchAdd"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)

    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    assert r.status_code == 404


# ── 8. Add template to archived pack ──


@pytest.mark.asyncio
async def test_add_template_to_archived_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ArchTmpl"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid)

    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)
    assert r.status_code == 404


# ── 9. Publish on archived pack ──


@pytest.mark.asyncio
async def test_publish_release_on_archived_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, _ = await _pack_with_skill(c, h, oid, "ArchPub", "ArchPubSk")

    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 404


# ── 10. Cross-org template ──


@pytest.mark.asyncio
async def test_add_cross_org_template(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "XTmpl"}, headers=h1)).json()["data"]["id"]
    tid = await _template(c, h2, oid2)  # template in org2

    r = await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/templates", json={"template_id": tid}, headers=h1)
    assert r.status_code == 404


# ── 11. List pack templates ──


@pytest.mark.asyncio
async def test_list_pack_templates(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ListT"}, headers=h)).json()["data"]["id"]
    t1 = await _template(c, h, oid, "Template A")
    t2 = await _template(c, h, oid, "Template B")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": t1, "sort_order": 0}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": t2, "sort_order": 1}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/templates", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["data"][0]["template_name"] == "Template A"


# ── 12. Get release not found ──


@pytest.mark.asyncio
async def test_get_release_not_found(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, _ = await _pack_with_skill(c, h, oid, "NoVer", "NoVerSk")

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/99.99.99", headers=h)
    assert r.status_code == 404


# ── 13. Cross-org pack update ──


@pytest.mark.asyncio
async def test_cross_org_pack_update(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "XUpdate"}, headers=h1)).json()["data"]["id"]

    r = await c.put(f"/api/v1/orgs/{oid2}/packs/{pid}", json={"name": "Hacked"}, headers=h2)
    assert r.status_code == 404


# ── 14. Cross-org pack delete ──


@pytest.mark.asyncio
async def test_cross_org_pack_delete(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "XDelete"}, headers=h1)).json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{oid2}/packs/{pid}", headers=h2)
    assert r.status_code == 404


# ── 15. Cross-org add skill ──


@pytest.mark.asyncio
async def test_cross_org_pack_add_skill(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "XAddSk"}, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h2, oid2)

    r = await c.post(f"/api/v1/orgs/{oid2}/packs/{pid}/skills", json={"skill_id": sid}, headers=h2)
    assert r.status_code in (403, 404)


# ── 16. Cross-org publish release ──


@pytest.mark.asyncio
async def test_cross_org_pack_publish_release(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid, _ = await _pack_with_skill(c, h1, oid1, "XPub", "XPubSk")

    r = await c.post(f"/api/v1/orgs/{oid2}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h2)
    assert r.status_code in (403, 404)


# ── 17. Student cannot update pack ──


@pytest.mark.asyncio
async def test_student_cannot_update_pack(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "StuUpd"}, headers=h)).json()["data"]["id"]

    r = await c.put(f"/api/v1/orgs/{oid}/packs/{pid}", json={"name": "Nope"}, headers=hs)
    assert r.status_code == 403


# ── 18. Student cannot delete pack ──


@pytest.mark.asyncio
async def test_student_cannot_delete_pack(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "StuDel"}, headers=h)).json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=hs)
    assert r.status_code == 403


# ── 19. Student cannot publish release ──


@pytest.mark.asyncio
async def test_student_cannot_publish_release(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)
    pid, _ = await _pack_with_skill(c, h, oid, "StuPub", "StuPubSk")

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=hs)
    assert r.status_code == 403


# ── 20. Student cannot add skill ──


@pytest.mark.asyncio
async def test_student_cannot_add_skill(c):
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "StuAddSk"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid)

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=hs)
    assert r.status_code == 403


# ═══════════════ Pack list filters + pagination ═══════════════


@pytest.mark.asyncio
async def test_list_packs_filter_by_status_draft(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create one draft pack (stays draft)
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Draft Pack"}, headers=h)

    # Create one published pack (add skill + release)
    pid2 = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Published Pack"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Filter Skill")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid2}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid2}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs", params={"status": "draft"}, headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["status"] == "draft"


@pytest.mark.asyncio
async def test_list_packs_filter_by_status_published(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Draft pack
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Draft Only"}, headers=h)

    # Published pack
    pid2 = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Pub Only"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Pub Skill")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid2}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid2}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs", params={"status": "published"}, headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["status"] == "published"


@pytest.mark.asyncio
async def test_list_packs_excludes_archived(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Soon Archived"}, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Still Alive"}, headers=h)

    # Archive the first pack
    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1
    assert r.json()["data"][0]["name"] == "Still Alive"


@pytest.mark.asyncio
async def test_list_packs_pagination(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Page A"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Page B"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Page C"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs", params={"page": 2, "per_page": 2}, headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["meta"]["total"] == 3
    assert r.json()["meta"]["page"] == 2


# ═══════════════ Remove not-in-pack ═══════════════


@pytest.mark.asyncio
async def test_remove_skill_not_in_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "NoSkill"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Orphan Skill")

    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}/skills/{sid}", headers=h)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_IN_PACK"


@pytest.mark.asyncio
async def test_remove_template_not_in_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "NoTmpl"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid, "Orphan Template")

    r = await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}/templates/{tid}", headers=h)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_IN_PACK"


# ═══════════════ Publish edge cases ═══════════════


@pytest.mark.asyncio
async def test_publish_release_archived_template(c):
    """COMPONENT_ARCHIVED is defense-in-depth: the DELETE endpoint now
    detaches the template from packs (making the pack EMPTY_PACK instead),
    so archive directly in the DB to exercise the publish-time guard."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ArchTmplPub"}, headers=h)).json()["data"]["id"]
    tid = await _template(c, h, oid, "Doomed Template")
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/templates", json={"template_id": tid}, headers=h)

    # Archive the template directly (bypassing the endpoint's join-row
    # cleanup) — simulates any archival path that misses the pack detach
    from app.core.database import AsyncSessionLocal
    from app.models.project import ProjectTemplate
    from app.models.skill import ContentStatus

    async with AsyncSessionLocal() as db:
        tmpl = await db.get(ProjectTemplate, tid)
        tmpl.status = ContentStatus.ARCHIVED
        await db.commit()

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "COMPONENT_ARCHIVED"


@pytest.mark.asyncio
async def test_publish_release_manifest_exercise_content(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "ExPack"}, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, "Exercise Skill")

    # Create an exercise on the skill
    ex_r = await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/exercises", json={
        "title": "Quiz 1", "description": "First quiz", "type": "multiple_choice",
        "config": {"options": ["a", "b"], "correct": "a"}, "max_score": 50,
    }, headers=h)
    assert ex_r.status_code == 201

    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0", headers=h)
    assert r.status_code == 200
    ex = r.json()["data"]["manifest"]["skills"][0]["exercises"][0]
    assert ex["title"] == "Quiz 1"
    assert ex["type"] == "multiple_choice"
    assert ex["max_score"] == 50


# ═══════════════ Schema validation ═══════════════


@pytest.mark.asyncio
async def test_create_pack_name_too_short(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "A"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_pack_name_too_long(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "A" * 201}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_pack_summary_too_long(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Valid Name", "summary": "A" * 501}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_pack_invalid_visibility(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Bad Vis", "visibility": "internal"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_pack_invalid_difficulty(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Bad Diff", "difficulty": "novice"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_pack_invalid_visibility(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "UpdVis"}, headers=h)).json()["data"]["id"]

    r = await c.put(f"/api/v1/orgs/{oid}/packs/{pid}", json={"visibility": "restricted"}, headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_publish_release_version_too_long(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, _ = await _pack_with_skill(c, h, oid, "LongVer", "LongVerSk")

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "A" * 21}, headers=h)
    assert r.status_code == 422


# ═══════════════ State transitions + cascade ═══════════════


@pytest.mark.asyncio
async def test_archived_pack_cannot_be_reactivated(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Reactivate"}, headers=h)).json()["data"]["id"]

    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.put(f"/api/v1/orgs/{oid}/packs/{pid}", json={"status": "draft"}, headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_skill_in_pack_still_listed(c):
    """Archiving a skill excludes it from the pack skills listing."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid, sid = await _pack_with_skill(c, h, oid, "CascPack", "CascSkill")

    # Archive the skill
    await c.delete(f"/api/v1/orgs/{oid}/skills/{sid}", headers=h)

    # list_pack_skills joins with Skill and filters out archived
    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/skills", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 0
