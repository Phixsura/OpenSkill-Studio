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
    await _mock_offering(c, h2, o2)
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
    # org2 connected a mock offering (required to pass the install capability
    # gate — R44 derives requires_capabilities from provider_action steps),
    # so the suggestion resolves it rather than recording a gap
    assert any(r["code"] == "AUTO_SUGGESTED" for r in bindings[0]["reasons"])
    assert bindings[0]["gaps"] == []


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
    await _mock_offering(c, h, oid)
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
    await _mock_offering(c, h1, o1)
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
    await _mock_offering(c, h, oid)
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
    await _mock_offering(c, h, oid)
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
    await _mock_offering(c, h, oid)
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
    await _mock_offering(c, h, oid)  # satisfies the install capability gate
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

    await _mock_offering(c, h, oid)
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
    await _mock_offering(c, h1, o1)
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


# ── Audit fixes: confirmed-binding preservation + stable-latest ──


@pytest.mark.asyncio
async def test_upgrade_preserves_confirmed_binding(c):
    """Human-confirmed bindings survive an upgrade when the step and its
    capability are unchanged (audit fix — upgrades must not silently discard
    explicit provider choices)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "1.1.0"))
    offering_id = await _mock_offering(c, h, oid)

    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h,
    )
    install_id = r.json()["data"]["id"]

    # Confirm the binding for the provider_action step ("generate")
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/bindings/generate",
        json={"offering_id": offering_id, "binding_mode": "preferred"},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["data"]["confirmed_by"] is not None

    # Upgrade — same definition in 1.1.0, so the binding must be preserved
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/upgrade",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert r3.status_code == 200, r3.text

    r4 = await c.get(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/bindings", headers=h
    )
    binding = next(b for b in r4.json()["data"] if b["step_id"] == "generate")
    assert binding["confirmed_by"] is not None  # preserved, not wiped
    assert binding["offering_id"] == offering_id


@pytest.mark.asyncio
async def test_install_without_version_prefers_stable(c):
    """Implicit 'latest' must resolve to the stable release, not a newer
    pre-release (npm dist-tag semantics)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "1.1.0-beta.1"))
    await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations",
        json={"pack_id": pid},
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert r.json()["data"]["installed_version"] == "1.0.0"


# ── Audit fixes (Issue #21 follow-up) ─────────────────────


@pytest.mark.asyncio
async def test_installation_detail_returns_input_schema(c):
    """Run form for PRIVATE packs breaks without the definition's inputs —
    the installation detail endpoint must expose input_schema (audit HIGH 2)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Private (unapproved) pack — the registry preview is NOT available
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "Priv IS"}, headers=h)
    pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await _mock_offering(c, h, oid)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r2.json()["data"]["id"]

    r3 = await c.get(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}", headers=h)
    assert r3.status_code == 200
    schema = r3.json()["data"]["input_schema"]
    assert schema, "input_schema must be populated on the detail endpoint"
    assert schema[0]["key"] == "topic"
    assert schema[0]["type"] == "text"
    assert schema[0]["required"] is True

    # List endpoint stays lean (schema not resolved per row)
    r4 = await c.get(f"/api/v1/orgs/{oid}/workflow-installations", headers=h)
    assert all(row["input_schema"] == [] for row in r4.json()["data"])


@pytest.mark.asyncio
async def test_install_race_integrity_error_maps_to_409(c):
    """A concurrent install losing the unique-index race must surface 409
    ALREADY_INSTALLED, not a 500 (audit MEDIUM 9 — TOCTOU)."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)

    # Seed a conflicting row directly so the service's pre-check misses it
    # is impossible via API; instead call the service with a stale session
    # state: pre-insert the row AFTER the service's existence check by
    # simulating the outcome — insert first, then call install() which
    # will pass its own check only if we bypass it. Simplest determinis-
    # tic reproduction: two service calls on one session, second one's
    # pre-check sees nothing because we expunge the row from identity map.
    await _mock_offering(c, h, oid)
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.services.workflow_installation import WorkflowInstallationService

    async with AsyncSessionLocal() as db:
        svc = WorkflowInstallationService(db)
        install = await svc.install(oid, pid, None, u["id"])
        await db.commit()
        first_id = install.id

    async with AsyncSessionLocal() as db:
        svc = WorkflowInstallationService(db)
        # Monkeypatch the pre-check SELECT to simulate the race window:
        # the concurrent transaction's row isn't visible yet.
        orig_execute = db.execute

        async def patched(stmt, *a, **kw):
            res = await orig_execute(stmt, *a, **kw)
            desc = getattr(stmt, "column_descriptions", None)
            if desc and desc[0].get("type") is WorkflowPackInstallation:

                class _Empty:
                    def scalar_one_or_none(self):
                        return None

                return _Empty()
            return res

        db.execute = patched
        try:
            with pytest.raises(AppError) as exc_info:
                await svc.install(oid, pid, None, u["id"])
        finally:
            db.execute = orig_execute
        assert exc_info.value.code == "ALREADY_INSTALLED"
        assert exc_info.value.status_code == 409

    # First installation is intact
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-installations/{first_id}", headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_upgrade_and_diff_recheck_pack_access(c):
    """If a pack goes PRIVATE after a cross-org install, upgrade and diff
    must re-apply access rules → 404 (audit MEDIUM 10)."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(c, h1, o1, versions=("1.0.0", "2.0.0"))

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    await _mock_offering(c, h2, o2)
    r = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h2,
    )
    assert r.status_code == 201, r.text
    install_id = r.json()["data"]["id"]

    # Owner flips the pack to PRIVATE
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackVisibility
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, pid)
        pack.visibility = PackVisibility.PRIVATE
        await db.commit()

    r2 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations/{install_id}/upgrade",
        json={"version": "2.0.0"},
        headers=h2,
    )
    assert r2.status_code == 404
    assert r2.json()["error"]["code"] == "WORKFLOW_PACK_NOT_FOUND"

    r3 = await c.get(
        f"/api/v1/orgs/{o2}/workflow-installations/{install_id}/diff?to=2.0.0", headers=h2
    )
    assert r3.status_code == 404

    # The OWNER org can still upgrade its own private pack
    await _mock_offering(c, h1, o1)
    r4 = await c.post(
        f"/api/v1/orgs/{o1}/workflow-installations", json={"pack_id": pid}, headers=h1
    )
    own_install = r4.json()["data"]["id"]
    r5 = await c.get(
        f"/api/v1/orgs/{o1}/workflow-installations/{own_install}/diff?to=2.0.0", headers=h1
    )
    assert r5.status_code == 200


@pytest.mark.asyncio
async def test_registry_rejected_public_pack_hidden(c):
    """A PUBLIC pack whose review_status regressed past 'approved' must 404
    on the registry detail/releases/preview endpoints (audit MEDIUM 11)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, pid)
        pack.review_status = "rejected"
        await db.commit()

    for path in (
        f"/api/v1/registry/workflow-packs/{pid}",
        f"/api/v1/registry/workflow-packs/{pid}/releases",
        f"/api/v1/registry/workflow-packs/{pid}/preview",
    ):
        r = await c.get(path)
        assert r.status_code == 404, f"{path}: {r.status_code}"


@pytest.mark.asyncio
async def test_preview_strips_pinned_binding_details(c):
    """The anonymous registry preview must not leak the author org's
    pinned_offering_id / binding_mode provider setup (audit MEDIUM 12)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    d = _definition()
    d["steps"][1]["config"]["binding_mode"] = "pinned"
    d["steps"][1]["config"]["pinned_offering_id"] = "01SECRETOFFERING0000000000"
    pid = await _public_pack(c, h, oid, definition=d)

    r = await c.get(f"/api/v1/registry/workflow-packs/{pid}/preview")
    assert r.status_code == 200
    preview = r.json()["data"]
    assert "01SECRETOFFERING0000000000" not in r.text
    for step in preview["definition"]["steps"]:
        cfg = step.get("config") or {}
        assert "pinned_offering_id" not in cfg
        assert "binding_mode" not in cfg


# ── Audit round 16: suggestion ordering, reactivation race, unlisted access ──


@pytest.mark.asyncio
async def test_binding_suggestion_prefers_null_cost_like_runtime(c):
    """The install-time suggestion must sort NULL-cost offerings FIRST —
    matching the runtime auto-resolver's nullsfirst() — so the suggested
    offering is the one the auto rung would actually pick."""
    from sqlalchemy import update as sa_update

    from app.core.database import AsyncSessionLocal
    from app.models.provider import ProviderModelOffering

    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Priced offering created FIRST (lower ULID) — under the old
    # NULL-cost-last ordering it would win the suggestion
    priced_id = await _mock_offering(c, h, oid)
    async with AsyncSessionLocal() as db:
        await db.execute(
            sa_update(ProviderModelOffering)
            .where(ProviderModelOffering.id == priced_id)
            .values(cost_per_call_usd=5.0)
        )
        await db.commit()
    free_id = await _mock_offering(c, h, oid)  # cost stays NULL

    pid = await _public_pack(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    assert r.status_code == 201, r.text
    install_id = r.json()["data"]["id"]

    r2 = await c.get(
        f"/api/v1/orgs/{oid}/workflow-installations/{install_id}/bindings", headers=h
    )
    binding = next(b for b in r2.json()["data"] if b["step_id"] == "generate")
    assert binding["offering_id"] == free_id  # NULL cost first, like the runtime


@pytest.mark.asyncio
async def test_reinstall_race_lost_reactivation_maps_to_409(c):
    """Two concurrent reinstalls of a REMOVED installation: the loser's
    status-guarded reactivation UPDATE hits rowcount 0 and must surface a
    clean 409 — never a double install_count bump."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPack, WorkflowPackInstallation
    from app.services.workflow_installation import WorkflowInstallationService

    h, u = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]
    r2 = await c.delete(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}", headers=h)
    assert r2.status_code == 204

    async with AsyncSessionLocal() as db_a:
        # Session A loads the row while it is still REMOVED (identity map now
        # holds the stale status — the classic pre-check race window)
        stale = await db_a.get(WorkflowPackInstallation, install_id)
        assert stale.status.value == "removed"

        # Session B reactivates and commits first (the race winner)
        async with AsyncSessionLocal() as db_b:
            svc_b = WorkflowInstallationService(db_b)
            won = await svc_b.install(oid, pid, None, u["id"])
            await db_b.commit()
            assert won.id == install_id

        # Session A's pre-check sees the stale REMOVED row and takes the
        # reactivation path — the guarded UPDATE must lose cleanly
        svc_a = WorkflowInstallationService(db_a)
        with pytest.raises(AppError) as exc_info:
            await svc_a.install(oid, pid, None, u["id"])
        assert exc_info.value.code == "ALREADY_INSTALLED"
        assert exc_info.value.status_code == 409

    # install_count bumped exactly once by the winner (1 install − 1 remove
    # + 1 reactivation = 1)
    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, pid)
        assert pack.install_count == 1

    # The winner's installation is intact and active
    r3 = await c.get(f"/api/v1/orgs/{oid}/workflow-installations/{install_id}", headers=h)
    assert r3.status_code == 200
    assert r3.json()["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_unlisted_rejected_pack_still_upgradable_like_install(c):
    """_check_pack_access must mirror install(): an UNLISTED pack is reachable
    by anyone holding the id regardless of review_status (the approval gate
    only guards PUBLIC registry discovery) — upgrade/diff must not 404 where
    a fresh install would succeed."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _public_pack(c, h1, o1, versions=("1.0.0", "2.0.0"))

    # Owner goes unlisted, then a definition change resets approval and a
    # re-review is rejected — review_status lands on "rejected"
    r = await c.put(
        f"/api/v1/orgs/{o1}/workflow-packs/{pid}",
        json={"visibility": "unlisted"},
        headers=h1,
    )
    assert r.status_code == 200
    from app.core.database import AsyncSessionLocal
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, pid)
        pack.review_status = "rejected"
        await db.commit()

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    # install() allows the unlisted pack cross-org…
    await _mock_offering(c, h2, o2)
    r2 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations",
        json={"pack_id": pid, "version": "1.0.0"},
        headers=h2,
    )
    assert r2.status_code == 201, r2.text
    install_id = r2.json()["data"]["id"]

    # …so upgrade and diff must apply the SAME rules (previously 404)
    r3 = await c.get(
        f"/api/v1/orgs/{o2}/workflow-installations/{install_id}/diff?to=2.0.0", headers=h2
    )
    assert r3.status_code == 200, r3.text
    r4 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations/{install_id}/upgrade",
        json={"version": "2.0.0"},
        headers=h2,
    )
    assert r4.status_code == 200, r4.text
    assert r4.json()["data"]["installed_version"] == "2.0.0"


@pytest.mark.asyncio
async def test_remove_race_double_delete_decrements_once(c):
    """R42: two concurrent removes of the same installation — the loser's
    status-guarded UPDATE hits rowcount 0 and 404s; install_count is
    decremented exactly once (unguarded writes decremented twice, driving
    the pack's install_count to -1/floor and skewing popularity scoring)."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPack, WorkflowPackInstallation
    from app.services.workflow_installation import WorkflowInstallationService

    h, u = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]
    # Second install from another org so install_count starts at 2 — a double
    # decrement would land at 0 and be indistinguishable from correct if it
    # started at 1 (greatest(...,0) floor masks the bug).
    h2, u2 = await _auth(c)
    oid2 = await _org(c, h2)
    await _mock_offering(c, h2, oid2)
    r2 = await c.post(
        f"/api/v1/orgs/{oid2}/workflow-installations", json={"pack_id": pid}, headers=h2
    )
    assert r2.status_code == 201, r2.text

    async with AsyncSessionLocal() as db_a:
        # Session A loads the row while it is still ACTIVE (stale identity map)
        stale = await db_a.get(WorkflowPackInstallation, install_id)
        assert stale.status.value == "active"

        # Session B removes and commits first (race winner)
        async with AsyncSessionLocal() as db_b:
            await WorkflowInstallationService(db_b).remove(install_id, oid)
            await db_b.commit()

        # Session A's get_installation passes on the stale row — the guarded
        # UPDATE must lose cleanly with 404, not decrement again
        with pytest.raises(AppError) as exc_info:
            await WorkflowInstallationService(db_a).remove(install_id, oid)
        assert exc_info.value.code == "INSTALLATION_NOT_FOUND"

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, pid)
        # 2 installs − exactly 1 remove = 1 (double decrement would give 0)
        assert pack.install_count == 1


@pytest.mark.asyncio
async def test_capability_gate_cannot_be_bypassed_by_omitting_deps(c):
    """R44: requires_capabilities is DERIVED from the definition's
    provider_action steps at publish time. Publishing with NO dependencies
    block (the default) must still produce a manifest whose install gate
    fires for orgs lacking the capability — the old code put the caller's
    (empty) list into the manifest verbatim, so the gate never ran and the
    failure surfaced only mid-run as NO_ELIGIBLE_PROVIDER."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    # _public_pack publishes WITHOUT a dependencies body — the bypass shape
    pid = await _public_pack(c, h1, o1)

    # The manifest must carry the derived requirement
    r = await c.get(f"/api/v1/registry/workflow-packs/{pid}/preview")
    assert r.status_code == 200, r.text
    reqs = r.json()["data"]["requires_capabilities"]
    assert {"capability": "image_generation", "features": []} in reqs

    # An org with no offerings is blocked at INSTALL time (not mid-run)
    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations", json={"pack_id": pid}, headers=h2
    )
    assert r2.status_code == 422, r2.text
    assert r2.json()["error"]["code"] == "CAPABILITY_UNSATISFIED"
    details = r2.json()["error"]["details"]
    assert any(d["capability"] == "image_generation" for d in details)

    # Declared features are UNIONED with step-derived ones, never replaced
    h3, _ = await _auth(c)
    o3 = await _org(c, h3)
    definition = _definition(capability="voice_generation")
    definition["outputs"] = [
        {"key": "final", "type": "image", "from_step": "generate", "from_port": "result"}
    ]
    pid2 = await _public_pack(
        c,
        h3,
        o3,
        definition=definition,
        dependencies={
            "requires_capabilities": [
                {"capability": "multimodal_review", "features": ["json_mode"]}
            ]
        },
    )
    r3 = await c.get(f"/api/v1/registry/workflow-packs/{pid2}/preview")
    reqs2 = r3.json()["data"]["requires_capabilities"]
    caps2 = {e["capability"] for e in reqs2}
    assert caps2 == {"multimodal_review", "voice_generation"}


@pytest.mark.asyncio
async def test_fork_remove_race_cannot_resurrect(c):
    """R55: fork's unguarded ORM status write raced remove — fork reads
    ACTIVE, remove's guarded UPDATE commits REMOVED, fork's flush then
    overwrites REMOVED with FORKED: a zombie installation with deleted
    bindings and an already-decremented install_count."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.services.workflow_installation import WorkflowInstallationService

    h, u = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]

    async with AsyncSessionLocal() as db_a:
        # Session A (fork) loads the row while it is ACTIVE
        stale = await db_a.get(WorkflowPackInstallation, install_id)
        assert stale.status.value == "active"

        # Session B removes and commits first
        async with AsyncSessionLocal() as db_b:
            await WorkflowInstallationService(db_b).remove(install_id, oid)
            await db_b.commit()

        # Session A's fork must lose cleanly — 404, never a resurrection
        with pytest.raises(AppError) as exc_info:
            await WorkflowInstallationService(db_a).fork(install_id, oid)
        assert exc_info.value.code == "INSTALLATION_NOT_FOUND"
        await db_a.rollback()

    async with AsyncSessionLocal() as db:
        final = await db.get(WorkflowPackInstallation, install_id)
        assert final.status.value == "removed"  # stayed dead


@pytest.mark.asyncio
async def test_confirm_binding_rejects_offering_missing_required_features(c):
    """R61: confirm_binding validated capability but ignored the step's
    required_features. A human could confirm an offering missing a feature;
    the runtime's _resolve_offering then rejects it (feature-superset) and
    the step fails NO_ELIGIBLE_PROVIDER mid-run — the late surprise binding
    confirmation exists to prevent."""
    h, u = await _auth(c)
    oid = await _org(c, h)

    # Pack whose provider_action step demands a feature
    definition = _definition()
    gen = next(s for s in definition["steps"] if s["id"] == "generate")
    gen["config"] = {"capability": "image_generation", "required_features": ["hi_res"]}

    pid = await _public_pack(c, h, oid, definition=definition)
    # Offering WITH the feature (to pass the install gate)
    r = await c.get("/api/v1/providers/adapters", headers=h)
    aid = next(a for a in r.json()["data"] if a["key"] == "mock")["id"]
    conn = (
        await c.post(
            f"/api/v1/orgs/{oid}/provider-connections",
            json={"adapter_id": aid, "name": "Feat"},
            headers=h,
        )
    ).json()["data"]["id"]
    good = (
        await c.post(
            f"/api/v1/orgs/{oid}/provider-offerings",
            json={"connection_id": conn, "capability_key": "image_generation",
                  "model_name": "hi", "features": ["hi_res"]},
            headers=h,
        )
    ).json()["data"]["id"]
    # A second offering WITHOUT the feature
    bad = (
        await c.post(
            f"/api/v1/orgs/{oid}/provider-offerings",
            json={"connection_id": conn, "capability_key": "image_generation",
                  "model_name": "lo", "features": []},
            headers=h,
        )
    ).json()["data"]["id"]

    inst = (
        await c.post(f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h)
    ).json()["data"]["id"]

    # Confirming the feature-less offering is rejected
    rb = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{inst}/bindings/generate",
        json={"offering_id": bad, "binding_mode": "pinned"},
        headers=h,
    )
    assert rb.status_code == 422, rb.text[:200]
    assert rb.json()["error"]["code"] == "OFFERING_MISSING_FEATURES"

    # The feature-complete offering is accepted
    rg = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{inst}/bindings/generate",
        json={"offering_id": good, "binding_mode": "pinned"},
        headers=h,
    )
    assert rg.status_code == 200, rg.text[:200]


@pytest.mark.asyncio
async def test_upgrade_race_cannot_resurrect_removed(c):
    """R63: upgrade() used a bare ORM status write — a concurrent remove()
    could be overwritten, re-pointing a REMOVED install at a new release
    (same resurrection class as the R55 fork race)."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.services.workflow_installation import WorkflowInstallationService

    h, u = await _auth(c)
    oid = await _org(c, h)
    await _mock_offering(c, h, oid)
    pid = await _public_pack(c, h, oid, versions=("1.0.0", "2.0.0"))
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid, "version": "1.0.0"},
        headers=h,
    )
    install_id = r.json()["data"]["id"]

    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(WorkflowPackInstallation, install_id)
        assert stale.status.value == "active"
        async with AsyncSessionLocal() as db_b:
            await WorkflowInstallationService(db_b).remove(install_id, oid)
            await db_b.commit()
        with pytest.raises(AppError) as exc:
            await WorkflowInstallationService(db_a).upgrade(install_id, oid, "2.0.0")
        assert exc.value.code == "INSTALLATION_NOT_FOUND"
        await db_a.rollback()

    async with AsyncSessionLocal() as db:
        final = await db.get(WorkflowPackInstallation, install_id)
        assert final.status.value == "removed"


@pytest.mark.asyncio
async def test_confirm_binding_rejects_inactive_offering(c):
    """R63: confirm_binding accepted an inactive offering / disabled
    connection — the runtime rejects it, deferring NO_ELIGIBLE_PROVIDER to
    run time. Reject at confirm."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    await _mock_offering(c, h, oid)  # active, satisfies install gate

    # a SECOND, inactive offering for the same capability
    r = await c.get("/api/v1/providers/adapters", headers=h)
    aid = next(a for a in r.json()["data"] if a["key"] == "mock")["id"]
    conn = (await c.post(
        f"/api/v1/orgs/{oid}/provider-connections", json={"adapter_id": aid, "name": "C2"},
        headers=h,
    )).json()["data"]["id"]
    off = (await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={"connection_id": conn, "capability_key": "image_generation", "model_name": "off2"},
        headers=h,
    )).json()["data"]["id"]
    # deactivate it
    ru = await c.put(
        f"/api/v1/orgs/{oid}/provider-offerings/{off}", json={"is_active": False}, headers=h
    )
    assert ru.status_code == 200, ru.text

    inst = (await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )).json()["data"]["id"]
    rb = await c.put(
        f"/api/v1/orgs/{oid}/workflow-installations/{inst}/bindings/generate",
        json={"offering_id": off, "binding_mode": "pinned"},
        headers=h,
    )
    assert rb.status_code == 422, rb.text[:200]
    assert rb.json()["error"]["code"] == "OFFERING_INACTIVE"


@pytest.mark.asyncio
async def test_confirm_binding_race_cannot_orphan_on_removed_install(c):
    """R67: confirm_binding raced remove — get_installation read this
    session's pre-remove ACTIVE snapshot, so a blind binding insert landed
    AFTER remove's binding DELETE, orphaning a binding row on a removed
    installation (live-confirmed 6/8 races). confirm now row-locks the
    installation with a status != REMOVED guard (same lock order as remove),
    so a confirm losing the race cleanly 404s and writes nothing."""
    from sqlalchemy import func, select

    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import WorkflowStepBinding
    from app.services.workflow_installation import WorkflowInstallationService

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _public_pack(c, h, oid)
    offering_id = await _mock_offering(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-installations", json={"pack_id": pid}, headers=h
    )
    install_id = r.json()["data"]["id"]

    async with AsyncSessionLocal() as db_a:
        # Prime session A's identity map with the ACTIVE row so
        # confirm_binding's own get_installation returns the STALE cached
        # object (db.get hits the identity map, not the DB) — exactly the
        # live interleaving where confirm passed the ACTIVE check before
        # remove committed. Without this, get_installation would re-query and
        # see REMOVED on its own, masking whether the row-lock guard works.
        stale = await db_a.get(WorkflowPackInstallation, install_id)
        assert stale.status.value == "active"

        # Session B removes and commits (deletes bindings + flips REMOVED)
        async with AsyncSessionLocal() as db_b:
            await WorkflowInstallationService(db_b).remove(install_id, oid)
            await db_b.commit()

        # confirm must lose cleanly on the fresh-query row lock — 404, no insert
        with pytest.raises(AppError) as exc_info:
            await WorkflowInstallationService(db_a).confirm_binding(
                install_id,
                oid,
                step_id="generate",
                offering_id=offering_id,
                binding_mode="preferred",
                confirmed_by="u",
            )
        assert exc_info.value.code == "INSTALLATION_NOT_FOUND"
        await db_a.rollback()

    # No binding row survives on the removed installation
    async with AsyncSessionLocal() as db:
        count = await db.execute(
            select(func.count())
            .select_from(WorkflowStepBinding)
            .where(WorkflowStepBinding.installation_id == install_id)
        )
        assert count.scalar_one() == 0
