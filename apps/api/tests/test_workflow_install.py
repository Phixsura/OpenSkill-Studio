"""Tests for workflow installation, bindings, and the public workflow registry (ADR-010/011)."""

import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def c():
    from app.core.database import engine
    from app.main import app

    orig = app.router.lifespan_context

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


def _email():
    return f"wfi-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "WFI"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"I-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


def _definition(capability="image_generation"):
    return {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [{"key": "final", "type": "image", "from_step": "generate", "from_port": "result"}],
        "steps": [
            {
                "id": "build_prompt",
                "type": "prompt_template",
                "name": "Build prompt",
                "config": {"template": "About {{inputs.topic}}"},
                "inputs": [],
                "outputs": [{"port": "prompt", "type": "prompt"}],
            },
            {
                "id": "generate",
                "type": "provider_action",
                "name": "Generate",
                "config": {"capability": capability},
                "inputs": [{"port": "prompt", "type": "prompt"}],
                "outputs": [{"port": "result", "type": "image"}],
            },
        ],
        "edges": [
            {"id": "e1", "from_step": "build_prompt", "from_port": "prompt", "to_step": "generate", "to_port": "prompt"},
        ],
        "ui": {},
    }


async def _public_pack(c, h, oid, definition=None, versions=("1.0.0",), dependencies=None):
    """Create + define + publish + approve a pack (makes it PUBLIC)."""
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": f"Pub-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition or _definition()},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    for v in versions:
        body = {"version": v}
        if dependencies:
            body["dependencies"] = dependencies
        r3 = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json=body, headers=h
        )
        assert r3.status_code == 201, r3.text
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r4 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r4.status_code == 200
    return pid


async def _mock_offering(c, h, oid, capability="image_generation"):
    r = await c.get("/api/v1/providers/adapters", headers=h)
    aid = next(a for a in r.json()["data"] if a["key"] == "mock")["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": f"Mock-{uuid.uuid4().hex[:4]}"},
        headers=h,
    )
    conn_id = r2.json()["data"]["id"]
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={"connection_id": conn_id, "capability_key": capability, "model_name": "mock-v1"},
        headers=h,
    )
    return r3.json()["data"]["id"]


# ── Install ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_install_public_pack_from_other_org(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(c, h1, o1)

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations",
        json={"pack_id": pid},
        headers=h2,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["installed_version"] == "1.0.0"
    assert data["status"] == "active"

    # install_count incremented
    r2 = await c.get(f"/api/v1/registry/workflow-packs/{pid}")
    assert r2.json()["data"]["install_count"] == 1

    # Binding suggestion rows created for the provider_action step (unconfirmed)
    r3 = await c.get(
        f"/api/v1/orgs/{o2}/workflow-installations/{data['id']}/bindings", headers=h2
    )
    bindings = r3.json()["data"]
    assert len(bindings) == 1
    assert bindings[0]["step_id"] == "generate"
    assert bindings[0]["confirmed_by"] is None
    # No offering in org2 → gap recorded
    assert any(g["code"] == "NO_ELIGIBLE_PROVIDER" for g in bindings[0]["gaps"])


@pytest.mark.asyncio
async def test_install_capability_gate_unsatisfied(c):
    """Release requiring a capability the org lacks → 422 with structured gaps."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(
        c,
        h1,
        o1,
        dependencies={"requires_capabilities": [{"capability": "image_generation", "features": []}]},
    )

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations",
        json={"pack_id": pid},
        headers=h2,
    )
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "CAPABILITY_UNSATISFIED"
    assert err["details"][0]["capability"] == "image_generation"


@pytest.mark.asyncio
async def test_install_capability_gate_satisfied(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(
        c,
        h1,
        o1,
        dependencies={"requires_capabilities": [{"capability": "image_generation", "features": []}]},
    )

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    await _mock_offering(c, h2, o2)  # org2 connects a provider FIRST (human action)
    r = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations",
        json={"pack_id": pid},
        headers=h2,
    )
    assert r.status_code == 201
    # Binding suggestion now points at the offering
    install_id = r.json()["data"]["id"]
    r2 = await c.get(
        f"/api/v1/orgs/{o2}/workflow-installations/{install_id}/bindings", headers=h2
    )
    assert r2.json()["data"][0]["offering_id"] is not None


@pytest.mark.asyncio
async def test_double_install_conflict(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    r1 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    assert r1.status_code == 201
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ALREADY_INSTALLED"


@pytest.mark.asyncio
async def test_private_pack_not_installable_cross_org(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    # Published but PRIVATE (no approval)
    r = await c.post(
        f"/api/v1/orgs/{o1}/workflow-packs", json={"name": "Private WF"}, headers=h1
    )
    pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{o1}/workflow-packs/{pid}/definition",
        json={"definition": _definition()},
        headers=h1,
    )
    await c.post(
        f"/api/v1/orgs/{o1}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1
    )

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations", json={"pack_id": pid}, headers=h2
    )
    assert r2.status_code == 404  # information-hiding: same code as nonexistent

    # But the OWNER org can install its own private pack
    r3 = await c.post(
        f"/api/v1/orgs/{o1}/workflow-installations", json={"pack_id": pid}, headers=h1
    )
    assert r3.status_code == 201


# ── Upgrade / rollback ────────────────────────────────────


@pytest.mark.asyncio
async def test_upgrade_and_rollback(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "1.1.0"))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h,
    )
    install_id = r.json()["data"]["id"]
    assert r.json()["data"]["installed_version"] == "1.0.0"

    # Upgrade
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/upgrade",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["installed_version"] == "1.1.0"

    # Rollback (same endpoint, older version)
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/upgrade",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r3.status_code == 200
    assert r3.json()["data"]["installed_version"] == "1.0.0"

    # Same version again → 409
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/upgrade",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r4.status_code == 409


@pytest.mark.asyncio
async def test_upgrade_forked_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "1.1.0"))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h,
    )
    install_id = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/fork", headers=h)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/upgrade",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "CANNOT_UPGRADE_FORKED"


# ── Fork / remove ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_fork_and_remove_reinstall(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]

    r2 = await c.post(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/fork", headers=h)
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "forked"

    # Remove → 404 afterwards
    r3 = await c.delete(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}", headers=h)
    assert r3.status_code == 204
    r4 = await c.get(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}", headers=h)
    assert r4.status_code == 404

    # Reinstall reactivates (unique org+pack row reused)
    r5 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    assert r5.status_code == 201
    assert r5.json()["data"]["id"] == install_id
    assert r5.json()["data"]["status"] == "active"


# ── Bindings ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_confirm_binding(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    offering_id = await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]

    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/bindings/generate",
        json={"offering_id": offering_id, "binding_mode": "pinned"},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    data = r2.json()["data"]
    assert data["offering_id"] == offering_id
    assert data["binding_mode"] == "pinned"
    assert data["confirmed_by"] is not None


@pytest.mark.asyncio
async def test_confirm_binding_capability_mismatch(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)  # step requires image_generation
    wrong_offering = await _mock_offering(c, h, oid, capability="voice_generation")
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/bindings/generate",
        json={"offering_id": wrong_offering},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "CAPABILITY_MISMATCH"


# ── Diff ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_compute_diff(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # v1.0.0 with base definition
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "Diff Pack"}, headers=h
    )
    pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    # v2.0.0: change template + add a review gate step
    d2 = _definition()
    d2["steps"][0]["config"]["template"] = "Changed {{inputs.topic}}"
    d2["steps"].append(
        {
            "id": "qa",
            "type": "review_gate",
            "name": "QA",
            "config": {"due_days": 7},
            "inputs": [{"port": "subject", "type": "image"}],
            "outputs": [{"port": "decision", "type": "selection"}],
        }
    )
    d2["edges"].append(
        {"id": "e2", "from_step": "generate", "from_port": "result", "to_step": "qa", "to_port": "subject"}
    )
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": d2},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "2.0.0"}, headers=h
    )

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h,
    )
    install_id = r2.json()["data"]["id"]

    r3 = await c.get(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/diff?to=2.0.0", headers=h
    )
    assert r3.status_code == 200
    diff = r3.json()["data"]
    assert diff["steps"]["added"] == ["qa"]
    assert diff["steps"]["changed"] == ["build_prompt"]
    assert diff["steps"]["removed"] == []
    assert diff["edges"]["added_count"] == 1


# ── Cross-org ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_installation_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(c, h1, o1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/workflow-installations", json={"pack_id": pid}, headers=h1
    )
    install_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/workflow-installations/{install_id}", headers=h2)
    assert r2.status_code == 404


# ── Public registry ───────────────────────────────────────


@pytest.mark.asyncio
async def test_registry_only_shows_public_approved(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    public_pid = await _public_pack(c, h, oid)

    # Private published pack — must NOT appear
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "Private One"}, headers=h
    )
    private_pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{private_pid}/definition",
        json={"definition": _definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{private_pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )

    r2 = await c.get("/api/v1/registry/workflow-packs?per_page=100")
    assert r2.status_code == 200
    ids = [p["id"] for p in r2.json()["data"]]
    assert public_pid in ids
    assert private_pid not in ids

    # Direct access to the private pack → 404
    r3 = await c.get(f"/api/v1/registry/workflow-packs/{private_pid}")
    assert r3.status_code == 404


@pytest.mark.asyncio
async def test_registry_filter_by_capability(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    img_pid = await _public_pack(c, h, oid, definition=_definition("image_generation"))
    await _public_pack(c, h, oid, definition=_definition("voice_generation"))

    r = await c.get("/api/v1/registry/workflow-packs?capability=image_generation&per_page=100")
    ids = [p["id"] for p in r.json()["data"]]
    assert img_pid in ids
    caps_lists = [p["capability_tags"] for p in r.json()["data"]]
    assert all("image_generation" in caps for caps in caps_lists)


@pytest.mark.asyncio
async def test_registry_preview_excludes_ui(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    d = _definition()
    d["ui"] = {"positions": {"build_prompt": [1, 2]}}
    pid = await _public_pack(c, h, oid, definition=d)

    r = await c.get(f"/api/v1/registry/workflow-packs/{pid}/preview")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "ui" not in data["definition"]
    assert data["step_count"] == 2
    assert data["inputs"][0]["key"] == "topic"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_registry_releases_no_manifest(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "1.1.0"))
    r = await c.get(f"/api/v1/registry/workflow-packs/{pid}/releases")
    assert r.status_code == 200
    data = r.json()["data"]
    assert [rel["version"] for rel in data] == ["1.1.0", "1.0.0"]
    assert "manifest" not in data[0]


@pytest.mark.asyncio
async def test_registry_search_and_output_type_filter(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    marker = uuid.uuid4().hex[:8]
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": f"Searchable {marker}", "summary": "video pipeline"},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)

    # Search by unique marker
    r2 = await c.get(f"/api/v1/registry/workflow-packs?search={marker}")
    assert [p["id"] for p in r2.json()["data"]] == [pid]

    # output_type=image matches (definition outputs image)
    r3 = await c.get(
        f"/api/v1/registry/workflow-packs?search={marker}&output_type=image"
    )
    assert [p["id"] for p in r3.json()["data"]] == [pid]

    # output_type=audio does not match
    r4 = await c.get(
        f"/api/v1/registry/workflow-packs?search={marker}&output_type=audio"
    )
    assert r4.json()["data"] == []
