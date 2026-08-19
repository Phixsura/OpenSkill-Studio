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
    r = await c.post("/api/v1/orgs", json={"name": f"P-{uuid.uuid4().hex[:6]}"}, headers=h)
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
    assert r.json()["error"]["code"] == "INVALID_VERSION"


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
