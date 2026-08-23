"""Tests for workflow pack CRUD / definition / releases / approval (ADR-010)."""

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
    return f"wfp-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "WFP"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"W-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201
    return r.json()["data"]["id"]


async def _pack(c, h, oid, name="Hero Image Workflow"):
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": name, "summary": "E-commerce hero image production", "workflow_type": "production"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]["id"]


def _valid_definition() -> dict:
    return {
        "schema_version": 1,
        "inputs": [{"key": "product_name", "type": "text", "required": True}],
        "outputs": [
            {"key": "hero", "type": "image", "from_step": "generate", "from_port": "result"}
        ],
        "steps": [
            {
                "id": "write_prompt",
                "type": "prompt_template",
                "name": "Build prompt",
                "config": {"template": "Photo of {{inputs.product_name}}"},
                "inputs": [],
                "outputs": [{"port": "prompt", "type": "prompt"}],
            },
            {
                "id": "generate",
                "type": "provider_action",
                "name": "Generate",
                "config": {"capability": "image_generation"},
                "inputs": [{"port": "prompt", "type": "prompt"}],
                "outputs": [{"port": "result", "type": "image"}],
            },
        ],
        "edges": [
            {
                "id": "e1",
                "from_step": "write_prompt",
                "from_port": "prompt",
                "to_step": "generate",
                "to_port": "prompt",
            }
        ],
        "ui": {"positions": {"write_prompt": [0, 0], "generate": [260, 0]}},
    }


# ── CRUD ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_and_get_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["name"] == "Hero Image Workflow"
    assert data["status"] == "draft"
    assert data["visibility"] == "private"
    assert data["workflow_type"] == "production"
    assert data["definition"] == {}


@pytest.mark.asyncio
async def test_list_packs_excludes_archived(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    p1 = await _pack(c, h, oid, "Keep Me")
    p2 = await _pack(c, h, oid, "Archive Me")
    await c.delete(f"/api/v1/orgs/{oid}/workflow-packs/{p2}", headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs", headers=h)
    ids = [p["id"] for p in r.json()["data"]]
    assert p1 in ids
    assert p2 not in ids


@pytest.mark.asyncio
async def test_update_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"summary": "Updated summary", "difficulty": "intermediate"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["summary"] == "Updated summary"
    assert r.json()["data"]["difficulty"] == "intermediate"


@pytest.mark.asyncio
async def test_cross_org_pack_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    pid = await _pack(c, h1, o1)

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.get(f"/api/v1/orgs/{o2}/workflow-packs/{pid}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_invalid_workflow_type_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "Bad", "workflow_type": "autonomous_agent"},
        headers=h,
    )
    assert r.status_code == 422


# ── Definition ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_definition_valid(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    # Derived caches
    assert data["input_schema"][0]["key"] == "product_name"
    assert data["output_schema"][0] == {"key": "hero", "type": "image"}
    # Capability tags derived from provider_action steps
    assert data["capability_tags"] == ["image_generation"]
    assert data["definition_updated_at"] is not None


@pytest.mark.asyncio
async def test_update_definition_cycle_rejected_with_details(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    d = _valid_definition()
    d["steps"][0]["inputs"] = [{"port": "loop", "type": "prompt", "required": False}]
    d["edges"].append(
        {"id": "e2", "from_step": "generate", "from_port": "result", "to_step": "write_prompt", "to_port": "loop"}
    )
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": d},
        headers=h,
    )
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "WF_VALIDATION_FAILED"
    codes = {d["code"] for d in err["details"]}
    # Both type mismatch (image→prompt) and cycle
    assert "WF_GRAPH_CYCLE" in codes


@pytest.mark.asyncio
async def test_validate_endpoint_dry_run(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    d = _valid_definition()
    d["edges"][0]["from_step"] = "ghost"
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/validate",
        json={"definition": d},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["valid"] is False
    assert any(e["code"] == "WF_EDGE_UNKNOWN_STEP" for e in data["errors"])


@pytest.mark.asyncio
async def test_validate_endpoint_valid_definition(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/validate",
        json={"definition": _valid_definition()},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["valid"] is True


# ── Releases ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_release_full_flow(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={
            "version": "1.0.0",
            "changelog": "Initial release",
            "dependencies": {
                "requires_capabilities": [{"capability": "image_generation", "features": []}],
                "recommended_packs": [
                    {"family": "skill_pack", "slug": "prompt-basics", "version": ">=1.0.0"}
                ],
            },
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    rel = r.json()["data"]
    assert rel["version"] == "1.0.0"
    assert len(rel["checksum"]) == 64  # sha256 hex
    assert rel["step_count"] == 2

    # First release publishes the pack
    r2 = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}", headers=h)
    assert r2.json()["data"]["status"] == "published"


@pytest.mark.asyncio
async def test_publish_empty_definition_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EMPTY_DEFINITION"


@pytest.mark.asyncio
async def test_publish_duplicate_version_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    r1 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r1.status_code == 201
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "VERSION_EXISTS"


@pytest.mark.asyncio
async def test_release_manifest_excludes_ui_block(c):
    """The ui block (editor layout) must not affect the release checksum."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    async def _publish_with_ui(positions):
        # Same name both times — slug gets a random suffix so no collision;
        # the manifest content is identical except for the ui block.
        pid = await _pack(c, h, oid, "UI Checksum Test")
        d = _valid_definition()
        d["ui"]["positions"] = positions
        await c.put(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
            json={"definition": d},
            headers=h,
        )
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": "1.0.0"},
            headers=h,
        )
        return r.json()["data"]["checksum"]

    ck1 = await _publish_with_ui({"write_prompt": [0, 0], "generate": [260, 0]})
    ck2 = await _publish_with_ui({"write_prompt": [999, 999], "generate": [1, 1]})
    assert ck1 == ck2  # layout changes never invalidate releases (R4)


@pytest.mark.asyncio
async def test_invalid_version_constraint_rejected(c):
    """R7: only X.Y.Z or >=X.Y.Z constraints allowed in dependencies."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={
            "version": "1.0.0",
            "dependencies": {
                "recommended_packs": [
                    {"family": "skill_pack", "slug": "x", "version": "^1.0.0"}  # npm caret — rejected
                ]
            },
        },
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_VERSION_CONSTRAINT"


@pytest.mark.asyncio
async def test_releases_sorted_semver_desc(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    for v in ["1.0.0", "1.10.0", "1.2.0"]:
        await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": v},
            headers=h,
        )
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", headers=h)
    versions = [rel["version"] for rel in r.json()["data"]]
    assert versions == ["1.10.0", "1.2.0", "1.0.0"]  # numeric semver, not lexicographic


# ── Approval workflow ─────────────────────────────────────


@pytest.mark.asyncio
async def test_approval_flow(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)

    r1 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    assert r1.status_code == 200
    assert r1.json()["data"]["review_status"] == "pending"

    # Double-submit → 409
    r2 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    assert r2.status_code == 409

    r3 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r3.status_code == 200
    assert r3.json()["data"]["review_status"] == "approved"
    assert r3.json()["data"]["visibility"] == "public"


@pytest.mark.asyncio
async def test_reject_with_reason(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/reject",
        json={"reason": "Steps lack review gates"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["review_status"] == "rejected"
    assert r.json()["data"]["rejection_reason"] == "Steps lack review gates"


@pytest.mark.asyncio
async def test_student_cannot_create_pack(c):
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    h_student, u_student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": u_student["id"], "role": "student"},
        headers=h_owner,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "Student Pack"},
        headers=h_student,
    )
    assert r.status_code == 403
