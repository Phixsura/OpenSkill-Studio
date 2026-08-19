"""Integration tests for pack installation, registry, diff, and fork."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"inst-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Inst"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"I-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


async def _pack_with_release(c, h, oid, name="Test Pack", visibility="public"):
    """Create a pack with a skill and publish v1.0.0."""
    # Create pack
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": name, "visibility": visibility,
    }, headers=h)).json()["data"]["id"]

    # Create category + skill
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"Cat-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]

    # Add skill to pack
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)

    # Publish
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    return pid


# ═══════════════ Registry ═══════════════


@pytest.mark.asyncio
async def test_registry_search_public(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _pack_with_release(c, h, oid, "Public Searchable", "public")

    r = await c.get("/api/v1/registry/packs?search=Searchable")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1
    assert any("Searchable" in p["name"] for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_excludes_private(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _pack_with_release(c, h, oid, "Private Hidden", "private")

    r = await c.get("/api/v1/registry/packs?search=Hidden")
    assert r.status_code == 200
    assert not any("Hidden" in p["name"] for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_excludes_draft(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Create pack but DON'T publish — stays draft
    await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Draft Pack", "visibility": "public"}, headers=h)

    r = await c.get("/api/v1/registry/packs?search=Draft")
    assert not any("Draft" in p["name"] for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_pack_detail(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Detail Pack")

    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Detail Pack"


@pytest.mark.asyncio
async def test_registry_releases(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Release Pack")

    r = await c.get(f"/api/v1/registry/packs/{pid}/releases")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["version"] == "1.0.0"


# ═══════════════ Installation ═══════════════


@pytest.mark.asyncio
async def test_install_pack(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Install Pack")

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 201
    assert r.json()["data"]["installed_version"] == "1.0.0"
    assert r.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_install_creates_skills_in_target_org(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Content Pack")

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    # Target org should now have skills
    r = await c.get(f"/api/v1/orgs/{oid2}/skills", headers=h2)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_install_duplicate_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Dup Install")

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_install_private_pack_rejected(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Private Install", "private")

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_install_count_incremented(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Count Pack")

    r_before = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}", headers=h1)
    count_before = r_before.json()["data"]["install_count"]

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    r_after = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}", headers=h1)
    assert r_after.json()["data"]["install_count"] == count_before + 1


@pytest.mark.asyncio
async def test_list_installations(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "List Pack")

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations", headers=h2)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1


# ═══════════════ Update Check + Diff ═══════════════


@pytest.mark.asyncio
async def test_update_check(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Update Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # No update yet
    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.json()["data"]["update_available"] is False

    # Publish v1.1.0
    sid2 = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "New Skill", "description": "d" * 10, "difficulty": "beginner",
        "category_id": (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "NewCat"}, headers=h1)).json()["data"]["id"],
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid2}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.1.0"}, headers=h1)

    # Now update available
    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.json()["data"]["update_available"] is True
    assert r.json()["data"]["latest_version"] == "1.1.0"


# ═══════════════ Fork ═══════════════


@pytest.mark.asyncio
async def test_fork_installation(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Fork Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid2}/installations/{iid}/fork", headers=h2)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "forked"


@pytest.mark.asyncio
async def test_fork_blocks_update(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Fork Block")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid2}/installations/{iid}/fork", headers=h2)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.json()["data"]["update_available"] is False
    assert r.json()["data"]["reason"] == "forked"


# ═══════════════ Remove ═══════════════


@pytest.mark.asyncio
async def test_remove_installation(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Remove Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.status_code == 204


# ═══════════════ Cross-org isolation ═══════════════


@pytest.mark.asyncio
async def test_cross_org_installation_access(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Iso Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid1}/installations", json={"pack_id": pid}, headers=h1)
    iid = inst_r.json()["data"]["id"]

    # Other org can't see this installation
    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.status_code == 404


# ═══════════════ Registry Filters & Pagination ═══════════════


@pytest.mark.asyncio
async def test_registry_filter_by_scenario(c):
    """Search with ?scenario=ecommerce finds pack tagged with that scenario."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Scenario Pack",
        "visibility": "public",
        "scenario_tags": ["ecommerce"],
    }, headers=h)).json()["data"]["id"]

    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"SC-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"SC-Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get("/api/v1/registry/packs?scenario=ecommerce")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_filter_by_tool(c):
    """Search with ?tool=comfyui finds pack tagged with that tool."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Tool Pack",
        "visibility": "public",
        "tool_tags": ["comfyui"],
    }, headers=h)).json()["data"]["id"]

    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"TL-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"TL-Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get("/api/v1/registry/packs?tool=comfyui")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_filter_by_difficulty(c):
    """Search with ?difficulty=beginner finds pack with that difficulty."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Difficulty Pack",
        "visibility": "public",
        "difficulty": "beginner",
    }, headers=h)).json()["data"]["id"]

    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"DF-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"DF-Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get("/api/v1/registry/packs?difficulty=beginner")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_sort_popular(c):
    """sort=most_installed puts pack with more installs first."""
    h1, _ = await _auth(c)
    oid1 = await _org(c, h1)
    less_pid = await _pack_with_release(c, h1, oid1, f"Less-{uuid.uuid4().hex[:6]}", "public")
    more_pid = await _pack_with_release(c, h1, oid1, f"More-{uuid.uuid4().hex[:6]}", "public")

    # Install the "more" pack multiple times from different orgs
    for _ in range(3):
        hx, _ = await _auth(c)
        ox = await _org(c, hx)
        await c.post(f"/api/v1/orgs/{ox}/installations", json={"pack_id": more_pid}, headers=hx)

    # Install the "less" pack once
    hy, _ = await _auth(c)
    oy = await _org(c, hy)
    await c.post(f"/api/v1/orgs/{oy}/installations", json={"pack_id": less_pid}, headers=hy)

    r = await c.get("/api/v1/registry/packs?sort=most_installed&per_page=100")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    if more_pid in ids and less_pid in ids:
        assert ids.index(more_pid) < ids.index(less_pid)


@pytest.mark.asyncio
async def test_registry_pagination(c):
    """page+per_page returns correct number of results and meta.total."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for i in range(3):
        await _pack_with_release(c, h, oid, f"Page-{uuid.uuid4().hex[:6]}-{i}", "public")

    r = await c.get("/api/v1/registry/packs?page=1&per_page=2")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["meta"]["total"] >= 3
    assert r.json()["meta"]["has_more"] is True


@pytest.mark.asyncio
async def test_registry_unlisted_not_in_search(c):
    """Unlisted packs do not appear in registry search results."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, f"Unlisted-{uuid.uuid4().hex[:6]}", "unlisted")

    r = await c.get("/api/v1/registry/packs?search=Unlisted")
    assert r.status_code == 200
    assert not any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_unlisted_accessible_by_id(c):
    """Unlisted pack is accessible via direct GET by ID."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Unlisted Direct", "unlisted")

    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 200
    assert r.json()["data"]["id"] == pid


@pytest.mark.asyncio
async def test_registry_private_pack_detail_rejected(c):
    """Private pack is not accessible via the public registry detail endpoint."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Private Detail", "private")

    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 404


# ═══════════════ Compute Diff ═══════════════


@pytest.mark.asyncio
async def test_compute_diff_added_skill(c):
    """Diff detects a skill added in the new release."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "DiffAdd Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Add a second skill to source pack and publish v2
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "DiffAddCat"}, headers=h1)).json()["data"]["id"]
    sid2 = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "Added Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid2}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert len(diff["added"]) >= 1
    assert any(a["type"] == "skill" for a in diff["added"])


@pytest.mark.asyncio
async def test_compute_diff_removed_skill(c):
    """Diff detects a skill removed in the new release."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack with TWO skills so removing one still allows publishing
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "DiffRm Pack", "visibility": "public"}, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "DiffRmCat"}, headers=h1)).json()["data"]["id"]
    sid_a = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "Keep Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    sid_b = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "Remove Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid_a}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid_b}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Remove one skill and publish v2
    await c.delete(f"/api/v1/orgs/{oid1}/packs/{pid}/skills/{sid_b}", headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert len(diff["removed"]) >= 1
    assert any(a["type"] == "skill" for a in diff["removed"])


@pytest.mark.asyncio
async def test_compute_diff_changed_skill(c):
    """Diff detects a skill changed between releases."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "DiffChg Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Edit the skill's description and publish v2
    pack_skills_r = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", headers=h1)
    original_sid = pack_skills_r.json()["data"][0]["skill_id"]
    await c.put(f"/api/v1/orgs/{oid1}/skills/{original_sid}", json={"description": "x" * 20}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert len(diff["changed"]) >= 1


@pytest.mark.asyncio
async def test_compute_diff_conflict_locally_modified(c):
    """Diff reports conflict when a skill is locally modified in the target org."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill import Skill as SkillModel

    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "DiffConflict Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Mark the installed skill as locally_modified directly in DB
    from sqlalchemy import select, update
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SkillModel).where(
                SkillModel.origin_pack_id == pid,
                SkillModel.org_id == oid2,
            )
        )
        installed_skill = result.scalar_one()
        await session.execute(
            update(SkillModel)
            .where(SkillModel.id == installed_skill.id)
            .values(locally_modified=True)
        )
        await session.commit()

    # Modify source skill and publish v2
    pack_skills_r = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", headers=h1)
    original_sid = pack_skills_r.json()["data"][0]["skill_id"]
    await c.put(f"/api/v1/orgs/{oid1}/skills/{original_sid}", json={"description": "y" * 20}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert len(diff["conflicts"]) >= 1
    assert diff["conflicts"][0]["reason"] == "locally_modified"


# ═══════════════ Install Edge Cases ═══════════════


@pytest.mark.asyncio
async def test_reinstall_after_removal(c):
    """After removing an installation, re-installing the same pack succeeds."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Reinstall Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]
    await c.delete(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_install_specific_version(c):
    """Install a specific older version when a newer one exists."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "VerPick Pack")

    # Publish v2
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "VP"}, headers=h1)).json()["data"]["id"]
    sid2 = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "VP Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid2}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid, "version": "1.0.0"}, headers=h2)
    assert r.status_code == 201
    assert r.json()["data"]["installed_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_install_pack_not_found(c):
    """Installing a pack with a fake ID returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/installations", json={"pack_id": "01JFAKE00000000000000FAKE"}, headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_install_no_release(c):
    """Installing a pack with no releases returns 404."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={
        "name": "NoRelease Pack", "visibility": "public",
    }, headers=h1)).json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_install_creates_exercises(c):
    """Installing a pack with exercises creates exercises in the target org."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack with a skill that has an exercise
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "ExPack", "visibility": "public"}, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "ExCat"}, headers=h1)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "Ex Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    # Create an exercise for this skill
    await c.post(f"/api/v1/orgs/{oid1}/skills/{sid}/exercises", json={
        "title": "Test Exercise", "description": "Do this", "type": "text_answer",
        "config": {}, "max_score": 100,
    }, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    # Verify exercises exist in target org's skills
    skills_r = await c.get(f"/api/v1/orgs/{oid2}/skills", headers=h2)
    target_sid = skills_r.json()["data"][0]["id"]
    ex_r = await c.get(f"/api/v1/orgs/{oid2}/skills/{target_sid}/exercises", headers=h2)
    assert ex_r.status_code == 200
    assert len(ex_r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_install_creates_project_templates(c):
    """Installing a pack with templates creates project templates in target org."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack with skill + template
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "TmplPack", "visibility": "public"}, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "TmplCat"}, headers=h1)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "Tmpl Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    tid = (await c.post(f"/api/v1/orgs/{oid1}/project-templates", json={
        "name": "Installed Template", "description": "Template desc",
        "instructions": "Do the thing",
        "rubric": [{"criterion": "Quality", "max_score": 100}],
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/templates", json={"template_id": tid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    # Verify project templates exist in target org
    tmpl_r = await c.get(f"/api/v1/orgs/{oid2}/project-templates", headers=h2)
    assert tmpl_r.status_code == 200
    assert len(tmpl_r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_install_unlisted_pack_succeeds(c):
    """Unlisted pack from another org can be installed (via direct ID)."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Unlisted Install", "unlisted")

    r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 201


# ═══════════════ Cross-org IDOR ═══════════════


@pytest.mark.asyncio
async def test_cross_org_fork_idor(c):
    """User cannot fork another org's installation."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "ForkIDOR Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid1}/installations", json={"pack_id": pid}, headers=h1)
    iid = inst_r.json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid2}/installations/{iid}/fork", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cross_org_remove_idor(c):
    """User cannot remove another org's installation."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "RmIDOR Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid1}/installations", json={"pack_id": pid}, headers=h1)
    iid = inst_r.json()["data"]["id"]

    r = await c.delete(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_cross_org_list_idor(c):
    """Listing installations for another org returns empty (not the other org's data)."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "ListIDOR Pack")

    await c.post(f"/api/v1/orgs/{oid1}/installations", json={"pack_id": pid}, headers=h1)

    # h2 lists org2's installations — should NOT contain org1's data
    r = await c.get(f"/api/v1/orgs/{oid2}/installations", headers=h2)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_fork_already_forked(c):
    """Forking an already-forked installation returns 422."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "DoubleFork Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    await c.post(f"/api/v1/orgs/{oid2}/installations/{iid}/fork", headers=h2)
    r = await c.post(f"/api/v1/orgs/{oid2}/installations/{iid}/fork", headers=h2)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_student_cannot_install(c):
    """Student role cannot install a pack."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)

    h_pub, _ = await _auth(c)
    oid_pub = await _org(c, h_pub)
    pid = await _pack_with_release(c, h_pub, oid_pub, "Student Install Pack")

    r = await c.post(f"/api/v1/orgs/{oid}/installations", json={"pack_id": pid}, headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_check_update_source_unavailable(c):
    """When pack_id is None on an installation, check_update returns source_unavailable."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPackInstallation as InstModel

    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Src Unavail Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Null out pack_id directly in DB to simulate source unavailable
    from sqlalchemy import update
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(InstModel)
            .where(InstModel.id == iid)
            .values(pack_id=None)
        )
        await session.commit()

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.status_code == 200
    assert r.json()["data"]["update_available"] is False
    assert r.json()["data"]["reason"] == "source_unavailable"
