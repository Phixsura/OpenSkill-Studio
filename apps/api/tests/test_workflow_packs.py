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


def test_parse_semver_prerelease_precedence():
    """Semver 2.0 §11: numeric prerelease identifiers compare NUMERICALLY
    (rc.10 > rc.9 — not lexicographic), numeric ranks below alphanumeric,
    a longer identifier list wins a shared prefix, and a release outranks
    every prerelease of the same X.Y.Z."""
    from app.services.workflow_pack import _parse_semver

    assert _parse_semver("1.0.0-rc.10") > _parse_semver("1.0.0-rc.9")
    assert _parse_semver("1.0.0") > _parse_semver("1.0.0-rc.10")
    # spec §11 example chain: alpha < alpha.1 < alpha.beta < beta < beta.2
    # < beta.11 < rc.1 < release
    ordered = [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
    ]
    keys = [_parse_semver(v) for v in ordered]
    assert keys == sorted(keys)
    # numeric identifiers rank below alphanumeric ones (1 < alpha)
    assert _parse_semver("1.0.0-1") < _parse_semver("1.0.0-alpha")
    # higher base version beats any prerelease state
    assert _parse_semver("1.0.1-alpha") > _parse_semver("1.0.0")


@pytest.mark.asyncio
async def test_releases_sorted_numeric_prerelease(c):
    """rc.10 must sort above rc.9 in the releases list (semver identifier
    comparison, not string comparison)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    for v in ["1.0.0-rc.9", "1.0.0-rc.10", "1.0.0"]:
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": v},
            headers=h,
        )
        assert r.status_code == 201, r.text
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", headers=h)
    versions = [rel["version"] for rel in r.json()["data"]]
    assert versions == ["1.0.0", "1.0.0-rc.10", "1.0.0-rc.9"]


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


# ── Audit fixes: approval bypass + re-approval on definition change ──


@pytest.mark.asyncio
async def test_visibility_public_requires_approval(c):
    """Direct PUT visibility=public on an unapproved pack must be rejected."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "public"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "APPROVAL_REQUIRED"

    # unlisted/private remain freely settable
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "unlisted"},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["visibility"] == "unlisted"

    # The approval flow still reaches public
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r3 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r3.json()["data"]["visibility"] == "public"

    # And once approved, PUT visibility=public is allowed (e.g. after
    # voluntarily going unlisted)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "unlisted"},
        headers=h,
    )
    r4 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "public"},
        headers=h,
    )
    assert r4.status_code == 200


@pytest.mark.asyncio
async def test_definition_change_resets_public_approval(c):
    """Editing the definition of an approved-public pack must force re-review
    so the public registry card can never drift from what was approved."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)

    # Change the definition post-approval
    d = _valid_definition()
    d["steps"][0]["config"]["template"] = "Changed {{inputs.product_name}}"
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": d},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["review_status"] is None
    assert data["visibility"] == "unlisted"


@pytest.mark.asyncio
async def test_definition_change_resets_approval_even_when_unlisted(c):
    """R15 HIGH: the approval reset must fire regardless of visibility.
    Otherwise an unlisted detour (public → unlisted → edit definition →
    public) carries 'approved' past the re-public gate and a changed
    definition reaches the public registry without re-review."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r_approve = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r_approve.json()["data"]["review_status"] == "approved"

    # Step 1: voluntarily go unlisted (no gate on downgrade)
    r1 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "unlisted"},
        headers=h,
    )
    assert r1.status_code == 200

    # Step 2: change the definition while unlisted — reset must still fire
    d = _valid_definition()
    d["steps"][0]["config"]["template"] = "Sneaky change {{inputs.product_name}}"
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": d},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["review_status"] is None

    # Step 3: PUT visibility=public must now be blocked — approval was voided
    r3 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "public"},
        headers=h,
    )
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "APPROVAL_REQUIRED"


# ── R15 batch B: input validation regressions ─────────────


@pytest.mark.asyncio
async def test_list_packs_invalid_status_422(c):
    """Unknown status values must 422 with INVALID_STATUS, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs?status=bogus", headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_STATUS"


@pytest.mark.asyncio
async def test_create_pack_invalid_language_422(c):
    """language column is String(10) — oversize/junk values must 422, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "Lang Test", "language": "this-is-way-too-long"},
        headers=h,
    )
    assert r.status_code == 422
    # Valid short code still works
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "Lang OK", "language": "pt-BR"},
        headers=h,
    )
    assert r2.status_code == 201, r2.text
    assert r2.json()["data"]["language"] == "pt-BR"


@pytest.mark.asyncio
async def test_update_pack_oversize_summary_422(c):
    """Update schema must mirror create-side length caps (String(500) column)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"summary": "x" * 501},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_pack_junk_difficulty_422(c):
    """Update schema must mirror the create-side difficulty enum."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"difficulty": "not-a-difficulty"},
        headers=h,
    )
    assert r.status_code == 422
    # Oversize tags also rejected on update
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"scenario_tags": ["x" * 51]},
        headers=h,
    )
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_publish_release_version_over_50_chars_422(c):
    """Version column is String(50) — a long-but-valid semver must 422, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    long_version = "1.0.0-" + "a" * 54  # 60 chars, matches the semver regex
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": long_version},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_publish_release_non_list_dependencies_422(c):
    """Non-list/non-dict JSON in the dependencies section must 422, not TypeError → 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    bad_dependencies = [
        {"requires_capabilities": "nope"},  # non-list value
        {"requires_capabilities": 5},  # int → len() TypeError before fix
        {"requires_capabilities": [{"capability": {}}]},  # non-str capability
        {"requires_capabilities": [{"capability": "image_generation", "features": 5}]},  # non-list features
        {"requires_capabilities": [{"capability": "image_generation", "features": [7]}]},  # non-str feature
        {"recommended_packs": "nope"},  # non-list value
    ]
    for deps in bad_dependencies:
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": "1.0.0", "dependencies": deps},
            headers=h,
        )
        assert r.status_code == 422, f"{deps} → {r.status_code} {r.text}"
        assert r.json()["error"]["code"] == "INVALID_DEPENDENCY"


@pytest.mark.asyncio
async def test_control_chars_rejected_in_text_fields(c):
    """NUL/control chars crash asyncpg with a 500 — reject at the schema
    boundary. Tab/newline/CR remain legal in multi-line fields."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # NUL in name → 422
    r1 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "bad\x00name"},
        headers=h,
    )
    assert r1.status_code == 422

    # BEL in changelog → 422
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0", "changelog": "note\x07here"},
        headers=h,
    )
    assert r2.status_code == 422

    # Newlines in description stay valid
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "Multiline OK", "description": "line one\nline two\n\tindented"},
        headers=h,
    )
    assert r3.status_code == 201, r3.text

    # NUL in update summary → 422
    r4 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"summary": "bad\x00summary"},
        headers=h,
    )
    assert r4.status_code == 422


def test_decide_review_note_rejects_control_chars():
    """DecideReviewRequest.note goes straight to a text column — NUL and
    control chars must fail schema validation (tab/newline stay legal)."""
    import pydantic

    from app.schemas.workflow_run import DecideReviewRequest

    with pytest.raises(pydantic.ValidationError):
        DecideReviewRequest(decision="approved", note="bad\x00note")
    with pytest.raises(pydantic.ValidationError):
        DecideReviewRequest(decision="rejected", note="bad\x07note")
    ok = DecideReviewRequest(decision="approved", note="line one\nline two")
    assert ok.note == "line one\nline two"


@pytest.mark.asyncio
async def test_latest_release_prefers_stable_over_prerelease(c):
    """A newer pre-release must not shadow the stable release for implicit installs."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    for v in ["1.0.0", "1.1.0-beta.1"]:
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": v},
            headers=h,
        )
        assert r.status_code == 201, r.text

    from app.core.database import AsyncSessionLocal
    from app.services.workflow_pack import WorkflowPackService

    async with AsyncSessionLocal() as db:
        svc = WorkflowPackService(db)
        latest = await svc.get_latest_release(pid)
        assert latest is not None
        assert latest.version == "1.0.0"  # stable wins over 1.1.0-beta.1


@pytest.mark.asyncio
async def test_recommended_pack_version_and_slug_type_checked(c):
    """R18: the R16 shape gate missed recommended_packs.version — a non-str
    value reached _VERSION_CONSTRAINT_RE.match() and TypeError'd into a 500.
    Same for non-str slug."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    for deps, expected_code in [
        ({"recommended_packs": [{"family": "skill_pack", "version": 1}]}, "INVALID_VERSION_CONSTRAINT"),
        ({"recommended_packs": [{"family": "skill_pack", "version": ["x"]}]}, "INVALID_VERSION_CONSTRAINT"),
        ({"recommended_packs": [{"family": "skill_pack", "slug": 42}]}, "INVALID_DEPENDENCY"),
    ]:
        r = await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": "1.0.0", "dependencies": deps},
            headers=h,
        )
        assert r.status_code == 422, f"{deps} → {r.status_code} {r.text}"
        assert r.json()["error"]["code"] == expected_code


@pytest.mark.asyncio
async def test_card_field_update_resets_approval(c):
    """R18: the approval-reset invariant covered only the definition path —
    update_pack let an approved PUBLIC pack rewrite every registry-facing
    card field (name/summary/tags) while keeping approved+public."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r.status_code == 200, r.text
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "public"},
        headers=h,
    )
    assert r.status_code == 200, r.text
    # Rewriting the public card voids the approval and pulls the pack back
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"name": "Completely Different Product", "summary": "new pitch"},
        headers=h,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["review_status"] is None
    assert data["visibility"] == "unlisted"
    # And public is gated again
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "public"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "APPROVAL_REQUIRED"


@pytest.mark.asyncio
async def test_tags_and_import_name_and_idem_key_reject_ctrl(c):
    """R18 sibling-gap closures: tags, ComfyUI import name, idempotency_key."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "T", "scenario_tags": ["ok", "bad\x00tag"]},
        headers=h,
    )
    assert r.status_code == 422
    pid = await _pack(c, h, oid, name="Ctrl Pack")
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"tool_tags": ["x\x07y"]},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_oversized_page_param_422_not_500(c):
    """R25 fuzz finding: page beyond int64 (or beyond the 1M bound) reached
    the SQL OFFSET as a bigint overflow → asyncpg DataError → 500. Every
    paginated list must reject an out-of-range page with 422, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for bad in ("999999999999999999999", "1000001", "-1", "0"):
        r = await c.get(
            f"/api/v1/orgs/{oid}/workflow-packs", params={"page": bad}, headers=h
        )
        assert r.status_code == 422, f"page={bad} -> {r.status_code}: {r.text[:150]}"
    # Upper bound accepted
    r = await c.get(
        f"/api/v1/orgs/{oid}/workflow-packs", params={"page": "1000000"}, headers=h
    )
    assert r.status_code == 200, r.text[:150]
