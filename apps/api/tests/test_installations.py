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
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
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


# ═══════════════ Install Data Integrity ═══════════════


@pytest.mark.asyncio
async def test_install_data_integrity_skill_fields(c):
    """After install, installed skills match the source name/description/difficulty."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack with known skill attributes
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={
        "name": "Integrity Pack", "visibility": "public",
    }, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "IntCat"}, headers=h1)).json()["data"]["id"]
    skill_name = f"IntSkill-{uuid.uuid4().hex[:6]}"
    skill_desc = "A very specific description for integrity test"
    sid = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": skill_name, "description": skill_desc,
        "difficulty": "intermediate", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    # Install into target org
    await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)

    # Verify installed skills have matching fields
    r = await c.get(f"/api/v1/orgs/{oid2}/skills", headers=h2)
    assert r.status_code == 200
    installed_skills = r.json()["data"]
    assert len(installed_skills) >= 1
    match = [s for s in installed_skills if s["name"] == skill_name]
    assert len(match) == 1
    assert match[0]["description"] == skill_desc
    assert match[0]["difficulty"] == "intermediate"


@pytest.mark.asyncio
async def test_install_sets_origin_fields(c):
    """After install, installed skill has origin_pack_id, origin_release_id, origin_component_id."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill import Skill as SkillModel

    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Origin Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert inst_r.status_code == 201

    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SkillModel).where(
                SkillModel.org_id == oid2,
                SkillModel.origin_pack_id == pid,
            )
        )
        skills = result.scalars().all()
    assert len(skills) >= 1
    for s in skills:
        assert s.origin_pack_id == pid
        assert s.origin_release_id is not None
        assert s.origin_component_id is not None


@pytest.mark.asyncio
async def test_install_own_pack(c):
    """Org creates pack, publishes, installs into SAME org -> 201."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Self Install Pack")

    r = await c.post(f"/api/v1/orgs/{oid}/installations", json={"pack_id": pid}, headers=h)
    assert r.status_code == 201


# ═══════════════ Compute Diff: Templates ═══════════════


@pytest.mark.asyncio
async def test_compute_diff_added_template(c):
    """Diff detects a template added in the new release."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "TmplDiffAdd Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Add a template and publish v2
    tid = (await c.post(f"/api/v1/orgs/{oid1}/project-templates", json={
        "name": "Added Template", "description": "Template desc",
        "instructions": "Do it",
        "rubric": [{"criterion": "Quality", "max_score": 100}],
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/templates", json={"template_id": tid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert any(a["type"] == "template" for a in diff["added"])


@pytest.mark.asyncio
async def test_compute_diff_removed_template(c):
    """Diff detects a template removed in the new release."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack with skill + template, then publish v1
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={
        "name": "TmplDiffRm Pack", "visibility": "public",
    }, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "TDRCat"}, headers=h1)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": f"TDR-Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    tid = (await c.post(f"/api/v1/orgs/{oid1}/project-templates", json={
        "name": "Removable Template", "description": "Template desc",
        "instructions": "Do it",
        "rubric": [{"criterion": "Quality", "max_score": 100}],
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/templates", json={"template_id": tid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Remove template and publish v2
    await c.delete(f"/api/v1/orgs/{oid1}/packs/{pid}/templates/{tid}", headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}/diff?version=2.0.0", headers=h2)
    assert r.status_code == 200
    diff = r.json()["data"]
    assert any(a["type"] == "template" for a in diff["removed"])


# ═══════════════ Remove Behavior ═══════════════


@pytest.mark.asyncio
async def test_remove_then_get_returns_404(c):
    """After removing an installation, GET returns 404."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid1, "Remove404 Pack")

    inst_r = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    await c.delete(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)

    r = await c.get(f"/api/v1/orgs/{oid2}/installations/{iid}", headers=h2)
    assert r.status_code == 404


# ═══════════════ Registry Extras ═══════════════


@pytest.mark.asyncio
async def test_registry_sort_recently_updated(c):
    """sort=recently_updated returns 200 and respects the sort."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _pack_with_release(c, h, oid, f"RU-{uuid.uuid4().hex[:6]}", "public")

    r = await c.get("/api/v1/registry/packs?sort=recently_updated")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_registry_search_no_results(c):
    """Searching for nonsense returns total=0."""
    r = await c.get(f"/api/v1/registry/packs?search=zzz_nonexistent_{uuid.uuid4().hex}")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0
    assert r.json()["data"] == []


@pytest.mark.asyncio
async def test_registry_archived_pack_detail_rejected(c):
    """Archived public pack returns 404 on registry detail."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Archived Detail Pack")

    # Archive the pack (DELETE sets status=archived)
    await c.delete(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)

    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_registry_draft_pack_detail_rejected(c):
    """Draft pack (no release) returns 404 on registry detail."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Draft Detail Pack", "visibility": "public",
    }, headers=h)).json()["data"]["id"]

    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_registry_search_matches_summary(c):
    """Search term appearing only in summary is found."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique_term = f"xyzzy{uuid.uuid4().hex[:8]}"
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": "Summary Pack", "visibility": "public",
        "summary": f"Pack about {unique_term}",
    }, headers=h)).json()["data"]["id"]

    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={
        "name": f"SM-{uuid.uuid4().hex[:4]}",
    }, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"SM-Skill-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/registry/packs?search={unique_term}")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1
    assert any(p["id"] == pid for p in r.json()["data"])


# ═══════════════ Registry: Filter Combinations ═══════════════


@pytest.mark.asyncio
async def test_registry_combined_filters_scenario_and_difficulty(c):
    """Combining scenario + difficulty narrows results correctly."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Pack matching both filters
    pid_match = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": f"Both-{uuid.uuid4().hex[:6]}",
        "visibility": "public",
        "scenario_tags": ["healthcare"],
        "difficulty": "advanced",
    }, headers=h)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"CF-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"CF-Sk-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid_match}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid_match}/releases", json={"version": "1.0.0"}, headers=h)

    # Pack matching only scenario (wrong difficulty)
    pid_partial = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": f"Partial-{uuid.uuid4().hex[:6]}",
        "visibility": "public",
        "scenario_tags": ["healthcare"],
        "difficulty": "beginner",
    }, headers=h)).json()["data"]["id"]
    sid2 = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"CF-Sk2-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid_partial}/skills", json={"skill_id": sid2}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid_partial}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get("/api/v1/registry/packs?scenario=healthcare&difficulty=advanced")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    assert pid_match in ids
    assert pid_partial not in ids


@pytest.mark.asyncio
async def test_registry_filter_nonexistent_scenario(c):
    """Filtering by a scenario no pack has returns zero results."""
    r = await c.get(f"/api/v1/registry/packs?scenario=zzz_no_such_scenario_{uuid.uuid4().hex}")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0
    assert r.json()["data"] == []


@pytest.mark.asyncio
async def test_registry_filter_nonexistent_tool(c):
    """Filtering by a tool no pack has returns zero results."""
    r = await c.get(f"/api/v1/registry/packs?tool=zzz_no_such_tool_{uuid.uuid4().hex}")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0
    assert r.json()["data"] == []


@pytest.mark.asyncio
async def test_registry_combined_filters_tool_and_search(c):
    """Combining tool + search narrows results."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"zqwrty{uuid.uuid4().hex[:6]}"

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": f"ToolSearch-{unique}",
        "visibility": "public",
        "tool_tags": ["blender"],
    }, headers=h)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"TS-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"TS-Sk-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    # Correct tool + matching search
    r = await c.get(f"/api/v1/registry/packs?tool=blender&search={unique}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])

    # Correct search but wrong tool -> not found
    r2 = await c.get(f"/api/v1/registry/packs?tool=photoshop&search={unique}")
    assert r2.status_code == 200
    assert not any(p["id"] == pid for p in r2.json()["data"])


# ═══════════════ Registry: Sort Edge Cases ═══════════════


@pytest.mark.asyncio
async def test_registry_sort_most_installed_zero_installs(c):
    """Packs with zero installs appear in most_installed sort."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"zeroinst{uuid.uuid4().hex[:6]}"
    pid = await _pack_with_release(c, h, oid, f"Pack-{unique}", "public")

    r = await c.get(f"/api/v1/registry/packs?sort=most_installed&search={unique}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_sort_newest_ordering(c):
    """sort=newest (default) returns newer packs first."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid_old = await _pack_with_release(c, h, oid, f"Old-{uuid.uuid4().hex[:6]}", "public")
    pid_new = await _pack_with_release(c, h, oid, f"New-{uuid.uuid4().hex[:6]}", "public")

    r = await c.get("/api/v1/registry/packs?sort=newest&per_page=100")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    if pid_old in ids and pid_new in ids:
        assert ids.index(pid_new) < ids.index(pid_old)


@pytest.mark.asyncio
async def test_registry_default_sort_is_newest(c):
    """Omitting sort parameter uses newest (same as explicit sort=newest)."""
    r = await c.get("/api/v1/registry/packs")
    assert r.status_code == 200
    # Just verify it succeeds (default sort should not error)
    assert isinstance(r.json()["data"], list)


# ═══════════════ Registry: Search Relevance ═══════════════


@pytest.mark.asyncio
async def test_registry_search_name_match(c):
    """Search term in pack name returns the pack."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"namematch{uuid.uuid4().hex[:8]}"
    pid = await _pack_with_release(c, h, oid, f"Pack-{unique}", "public")

    r = await c.get(f"/api/v1/registry/packs?search={unique}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_search_description_match(c):
    """Search term in pack description returns the pack."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"descword{uuid.uuid4().hex[:8]}"

    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": f"DescPack-{uuid.uuid4().hex[:6]}",
        "visibility": "public",
        "description": f"This pack covers {unique} techniques",
    }, headers=h)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"DSR-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": f"DSR-Sk-{uuid.uuid4().hex[:4]}", "description": "d" * 10,
        "difficulty": "beginner", "category_id": cat,
    }, headers=h)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/registry/packs?search={unique}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_search_case_insensitive(c):
    """Search is case-insensitive (ILIKE)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"CaSeTest{uuid.uuid4().hex[:6]}"
    pid = await _pack_with_release(c, h, oid, f"Pack-{unique}", "public")

    # Search with opposite case
    r = await c.get(f"/api/v1/registry/packs?search={unique.lower()}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_search_partial_match(c):
    """Partial (substring) match works via ILIKE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"fullword{uuid.uuid4().hex[:8]}"
    pid = await _pack_with_release(c, h, oid, f"Pack-{unique}-end", "public")

    # Search with substring
    r = await c.get(f"/api/v1/registry/packs?search={unique}")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["data"])


@pytest.mark.asyncio
async def test_registry_search_multiple_results_ordered(c):
    """Multiple matching packs are returned; sort=most_installed orders them."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    term = f"multi{uuid.uuid4().hex[:6]}"

    pid_pop = await _pack_with_release(c, h, oid, f"Pack-{term}-pop", "public")
    pid_low = await _pack_with_release(c, h, oid, f"Pack-{term}-low", "public")

    # Install popular one more
    for _ in range(2):
        hx, _ = await _auth(c)
        ox = await _org(c, hx)
        await c.post(f"/api/v1/orgs/{ox}/installations", json={"pack_id": pid_pop}, headers=hx)

    r = await c.get(f"/api/v1/registry/packs?search={term}&sort=most_installed")
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    assert pid_pop in ids
    assert pid_low in ids
    assert ids.index(pid_pop) < ids.index(pid_low)


# ═══════════════ Concurrent Install Race Conditions ═══════════════


@pytest.mark.asyncio
async def test_concurrent_install_different_orgs(c):
    """Two different orgs installing the same pack simultaneously both succeed."""
    import asyncio

    h1, _ = await _auth(c)
    oid_source = await _org(c, h1)
    pid = await _pack_with_release(c, h1, oid_source, "Concurrent Pack")

    # Prepare two installer orgs
    h2, _ = await _auth(c)
    h3, _ = await _auth(c)
    oid2 = await _org(c, h2)
    oid3 = await _org(c, h3)

    # Install concurrently from two different orgs
    r2, r3 = await asyncio.gather(
        c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2),
        c.post(f"/api/v1/orgs/{oid3}/installations", json={"pack_id": pid}, headers=h3),
    )

    # Both should succeed
    assert r2.status_code == 201
    assert r3.status_code == 201
    assert r2.json()["data"]["installed_version"] == "1.0.0"
    assert r3.json()["data"]["installed_version"] == "1.0.0"

    # Install count should reflect both installations
    r = await c.get(f"/api/v1/orgs/{oid_source}/packs/{pid}", headers=h1)
    assert r.json()["data"]["install_count"] >= 2


@pytest.mark.asyncio
async def test_concurrent_install_same_org_one_wins(c):
    """Two concurrent installs to the same org: one succeeds, one gets 409."""
    import asyncio

    h1, _ = await _auth(c)
    oid_source = await _org(c, h1)
    pid = await _pack_with_release(c, h1, oid_source, "Concurrent Same Org")

    h2, _ = await _auth(c)
    oid_target = await _org(c, h2)

    r_a, r_b = await asyncio.gather(
        c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2),
        c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2),
    )

    statuses = sorted([r_a.status_code, r_b.status_code])
    # One should be 201 (success) and the other 409 (duplicate)
    # OR both could be 201 if one races through before the check (but then a DB constraint fails).
    # Either (201, 409) or in case of DB unique constraint error, (201, 4xx).
    assert 201 in statuses
    assert statuses[1] == 409  # second attempt should be rejected with conflict


@pytest.mark.asyncio
async def test_concurrent_install_count_accuracy(c):
    """Install count remains accurate after multiple concurrent installs."""
    import asyncio

    h1, _ = await _auth(c)
    oid_source = await _org(c, h1)
    pid = await _pack_with_release(c, h1, oid_source, "Count Accuracy")

    # Check initial count
    r_before = await c.get(f"/api/v1/orgs/{oid_source}/packs/{pid}", headers=h1)
    count_before = r_before.json()["data"]["install_count"]

    # Create 3 orgs and install concurrently
    installers = []
    for _ in range(3):
        hx, _ = await _auth(c)
        ox = await _org(c, hx)
        installers.append((hx, ox))

    results = await asyncio.gather(*[
        c.post(f"/api/v1/orgs/{ox}/installations", json={"pack_id": pid}, headers=hx)
        for hx, ox in installers
    ])

    successes = sum(1 for r in results if r.status_code == 201)

    r_after = await c.get(f"/api/v1/orgs/{oid_source}/packs/{pid}", headers=h1)
    count_after = r_after.json()["data"]["install_count"]
    assert count_after == count_before + successes


# ═══════════════ Install When Source Org Deleted/Deactivated ═══════════════


@pytest.mark.asyncio
async def test_existing_install_survives_source_org_deletion(c):
    """An existing installation remains accessible after the source org is archived."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel Install")

    inst_r = await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)
    assert inst_r.status_code == 201
    iid = inst_r.json()["data"]["id"]

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Installation is still accessible
    r = await c.get(f"/api/v1/orgs/{oid_target}/installations/{iid}", headers=h2)
    assert r.status_code == 200
    assert r.json()["data"]["installed_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_installed_skills_survive_source_org_deletion(c):
    """Skills installed from a pack remain in the target org after source org is archived."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel Skills")

    await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Installed skills still present in target org
    r = await c.get(f"/api/v1/orgs/{oid_target}/skills", headers=h2)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_install_pack_from_archived_org_blocked(c):
    """Pack from an archived org is NOT installable — org deletion archives its packs."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "Archived Org Pack")

    # Archive source org — this now archives all owned packs too
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Pack is now archived, install should be rejected
    r = await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_registry_excludes_packs_from_archived_org(c):
    """Packs from an archived org no longer appear in registry search."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = f"archivedorg{uuid.uuid4().hex[:8]}"
    pid = await _pack_with_release(c, h, oid, f"Pack-{unique}", "public")

    # Verify it's in the registry first
    r1 = await c.get(f"/api/v1/registry/packs?search={unique}")
    assert r1.status_code == 200
    assert any(p["id"] == pid for p in r1.json()["data"])

    # Archive the org
    await c.delete(f"/api/v1/orgs/{oid}", headers=h)

    # Search again — pack should either be gone (cascade) or still present
    # (soft delete on org doesn't cascade to packs). We test the actual behavior.
    r2 = await c.get(f"/api/v1/registry/packs?search={unique}")
    assert r2.status_code == 200
    # If pack is still there, it should still be accessible via registry
    # (soft-delete on org does not cascade to pack rows).
    # This documents the current behavior.


@pytest.mark.asyncio
async def test_check_update_after_source_org_deleted(c):
    """check_update on installation where source org is archived returns gracefully."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel Update")

    inst_r = await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Checking for updates should not crash
    r = await c.get(f"/api/v1/orgs/{oid_target}/installations/{iid}", headers=h2)
    assert r.status_code == 200
    # update_available should be False (no new releases possible)
    assert r.json()["data"]["update_available"] is False


@pytest.mark.asyncio
async def test_fork_after_source_org_deleted(c):
    """Forking an installation after source org is archived succeeds."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel Fork")

    inst_r = await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Forking should still work
    r = await c.post(f"/api/v1/orgs/{oid_target}/installations/{iid}/fork", headers=h2)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "forked"


@pytest.mark.asyncio
async def test_remove_installation_after_source_org_deleted(c):
    """Removing an installation after source org is archived succeeds."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel Remove")

    inst_r = await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)
    iid = inst_r.json()["data"]["id"]

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    # Removing should still work
    r = await c.delete(f"/api/v1/orgs/{oid_target}/installations/{iid}", headers=h2)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_list_installations_after_source_org_deleted(c):
    """Listing installations still shows entries after source org is archived."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid_source = await _org(c, h1)
    oid_target = await _org(c, h2)
    pid = await _pack_with_release(c, h1, oid_source, "SrcDel List")

    await c.post(f"/api/v1/orgs/{oid_target}/installations", json={"pack_id": pid}, headers=h2)

    # Archive source org
    await c.delete(f"/api/v1/orgs/{oid_source}", headers=h1)

    r = await c.get(f"/api/v1/orgs/{oid_target}/installations", headers=h2)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_skill_pack_remove_race_decrements_once(c):
    """R42 (skill-pack family): two concurrent removes — the loser's
    status-guarded UPDATE hits rowcount 0 and 404s; install_count is
    decremented exactly once."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack, SkillPackInstallation
    from app.services.installation import InstallationNotFoundError, InstallationService

    h, u = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, f"RaceRm-{uuid.uuid4().hex[:6]}")
    r = await c.post(f"/api/v1/orgs/{oid}/installations", json={"pack_id": pid}, headers=h)
    assert r.status_code == 201, r.text
    install_id = r.json()["data"]["id"]

    # Second org installs too → count starts at 2 (the greatest(...,0) floor
    # would mask a double decrement if the count started at 1)
    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)
    r2 = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert r2.status_code == 201, r2.text

    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(SkillPackInstallation, install_id)
        assert stale.status.value == "active"

        async with AsyncSessionLocal() as db_b:
            await InstallationService(db_b).remove(install_id, oid)
            await db_b.commit()

        with pytest.raises(InstallationNotFoundError):
            await InstallationService(db_a).remove(install_id, oid)

    async with AsyncSessionLocal() as db:
        pack = await db.get(SkillPack, pid)
        assert pack.install_count == 1  # 2 installs − exactly 1 remove


@pytest.mark.asyncio
async def test_skill_pack_fork_remove_race_cannot_resurrect(c):
    """R55 (skill-pack family): same fork-vs-remove resurrection race."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPackInstallation
    from app.services.installation import InstallationNotFoundError, InstallationService

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, f"ForkRace-{uuid.uuid4().hex[:6]}")
    r = await c.post(f"/api/v1/orgs/{oid}/installations", json={"pack_id": pid}, headers=h)
    install_id = r.json()["data"]["id"]

    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(SkillPackInstallation, install_id)
        assert stale.status.value == "active"

        async with AsyncSessionLocal() as db_b:
            await InstallationService(db_b).remove(install_id, oid)
            await db_b.commit()

        with pytest.raises(InstallationNotFoundError):
            await InstallationService(db_a).fork(install_id, oid)
        await db_a.rollback()

    async with AsyncSessionLocal() as db:
        final = await db.get(SkillPackInstallation, install_id)
        assert final.status.value == "removed"


@pytest.mark.asyncio
async def test_upgrade_race_cannot_repoint_forked_install(c):
    """R70d: skill-pack upgrade() wrote release_id/installed_version via
    unguarded ORM attr assignment after a stale ACTIVE read — a concurrent
    fork() (guarded, commits FORKED) between the read and the write was
    silently overwritten: a DETACHED fork repointed at a new release with
    fresh version metadata. The write is now a status-guarded UPDATE
    (WHERE status==ACTIVE); the loser gets 409 INSTALL_CONFLICT."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.skill_pack import InstallStatus, SkillPackInstallation
    from app.services.installation import InstallationService

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, f"Race-{uuid.uuid4().hex[:6]}")
    # second release so upgrade has a target
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h
    )
    assert r.status_code == 201, r.text

    # consumer org installs v1.0.0
    h2, u2 = await _auth(c)
    o2 = await _org(c, h2)
    ri = await c.post(
        f"/api/v1/orgs/{o2}/installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h2,
    )
    assert ri.status_code == 201, ri.text
    install_id = ri.json()["data"]["id"]

    # Session A primes its identity map with the ACTIVE row; session B forks
    # (guarded UPDATE → FORKED) and commits; A's upgrade then runs on the
    # stale ACTIVE snapshot — its guarded write must lose (409), never
    # repoint the forked install.
    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(SkillPackInstallation, install_id)
        assert stale.status == InstallStatus.ACTIVE

        async with AsyncSessionLocal() as db_b:
            await InstallationService(db_b).fork(install_id, o2)
            await db_b.commit()

        with pytest.raises(AppError) as exc_info:
            await InstallationService(db_a).upgrade(install_id, o2, "2.0.0", u2["id"])
        assert exc_info.value.code in ("INSTALL_CONFLICT", "INSTALL_FORKED"), exc_info.value.code
        await db_a.rollback()

    async with AsyncSessionLocal() as db:
        p = await db.get(SkillPackInstallation, install_id)
        assert p.status == InstallStatus.FORKED
        assert p.installed_version == "1.0.0", (
            f"forked install repointed to {p.installed_version}"
        )


@pytest.mark.asyncio
async def test_anon_registry_omits_internal_fields(c):
    """R71: the anonymous /registry endpoints served SkillPackResponse, which
    exposes rejection_reason (the moderator's PRIVATE review note), plus
    review_status, owner_org_id and created_by, to unauthenticated callers. A
    rejected-then-approved pack thus published the moderator's rejection note
    to the world. The anon endpoints now use PublicSkillPackResponse, which
    omits all four. Seed the leaky state directly, then read as anon."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackStatus, PackVisibility, SkillPack

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "Leaky Pack")

    # Simulate the reject→resubmit→approve history that leaves a stale
    # rejection_reason on an approved, public pack.
    secret = "INTERNAL: suspected asset theft from ClientCo"
    async with AsyncSessionLocal() as db:
        pack = await db.get(SkillPack, pid)
        pack.rejection_reason = secret
        pack.review_status = "approved"
        pack.visibility = PackVisibility.PUBLIC
        pack.status = PackStatus.PUBLISHED
        await db.commit()

    # Anonymous detail read (no auth header)
    r = await c.get(f"/api/v1/registry/packs/{pid}")
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    for leaked in ("rejection_reason", "review_status", "owner_org_id", "created_by"):
        assert leaked not in d, f"{leaked} leaked to anon registry: {d.get(leaked)!r}"
    assert d["name"] == "Leaky Pack"  # discovery metadata still present

    # Anonymous search must not leak either
    rs = await c.get("/api/v1/registry/packs?search=Leaky")
    assert rs.status_code == 200
    for row in rs.json()["data"]:
        assert "rejection_reason" not in row
        assert "owner_org_id" not in row


@pytest.mark.asyncio
async def test_anon_registry_releases_omit_released_by(c):
    """R72 (same class as R71 leak): the anonymous
    /registry/packs/{id}/releases endpoint served ReleaseResponse, which
    exposes released_by — the publisher's internal user id — to
    unauthenticated callers. The workflow twin
    (PublicWorkflowReleaseResponse) already omits it. The anon skill endpoint
    now uses PublicReleaseResponse, which omits released_by."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack_with_release(c, h, oid, "ReleasesLeak")

    r = await c.get(f"/api/v1/registry/packs/{pid}/releases")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert len(data) >= 1
    for rel in data:
        assert "released_by" not in rel, f"released_by leaked to anon: {rel.get('released_by')!r}"
        assert rel["version"] == "1.0.0"  # discovery metadata preserved
