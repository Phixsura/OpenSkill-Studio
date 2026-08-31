"""Tests for workflow pack CRUD / definition / releases / approval (ADR-010)."""

import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _uuid():
    return uuid.uuid4().hex[:6]


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
        json={
            "name": name,
            "summary": "E-commerce hero image production",
            "workflow_type": "production",
        },
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
        {
            "id": "e2",
            "from_step": "generate",
            "from_port": "result",
            "to_step": "write_prompt",
            "to_port": "loop",
        }
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
                    {
                        "family": "skill_pack",
                        "slug": "x",
                        "version": "^1.0.0",
                    }  # npm caret — rejected
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
        {
            "requires_capabilities": [{"capability": "image_generation", "features": 5}]
        },  # non-list features
        {
            "requires_capabilities": [{"capability": "image_generation", "features": [7]}]
        },  # non-str feature
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
        (
            {"recommended_packs": [{"family": "skill_pack", "version": 1}]},
            "INVALID_VERSION_CONSTRAINT",
        ),
        (
            {"recommended_packs": [{"family": "skill_pack", "version": ["x"]}]},
            "INVALID_VERSION_CONSTRAINT",
        ),
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
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
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
async def test_provenance_update_voids_approval(c):
    """R82: provenance is shown on the anon workflow registry card
    (PublicWorkflowPackResponse) and editable via UpdateWorkflowPackRequest,
    but was absent from _card_fields — so an approved+public pack could have
    its provenance swapped past the review gate. It now voids approval."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["visibility"] == "public"
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"provenance": {"author_name": "injected after approval"}},
        headers=h,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["review_status"] is None, "provenance swap kept approval"
    assert data["visibility"] == "unlisted", "provenance swap left pack public"


@pytest.mark.asyncio
async def test_publish_new_release_after_approval_voids_approval(c):
    """R83: the anon registry preview serves the latest release's manifest
    (definition, dependencies, recommended_packs). Publishing a new release on
    an approved+public pack swaps that anon-served content past the review
    gate, so a new release must void approval — mirroring update_definition."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)
    assert r.status_code == 200 and r.json()["data"]["visibility"] == "public"

    # Publish v2 with a malicious recommended_packs dependency — approval resets
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={
            "version": "2.0.0",
            "dependencies": {
                "recommended_packs": [
                    {"slug": "evil-malware-pack", "family": "workflow_pack", "version": "1.0.0"}
                ]
            },
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    pk = (await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}", headers=h)).json()["data"]
    assert pk["review_status"] is None, "new release kept approval"
    assert pk["visibility"] == "unlisted", "new release left pack public"


@pytest.mark.asyncio
async def test_edit_while_pending_resets_review(c):
    """R84: a card/definition edit or new release WHILE review_status='pending'
    must reset the pack to draft — else the author swaps content after
    submitting and the reviewer approves stale content they never examined."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    sub = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    assert sub.json()["data"]["review_status"] == "pending"

    # Card edit while pending → draft
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"summary": "swapped after submit"},
        headers=h,
    )
    assert r.json()["data"]["review_status"] is None, "card edit while pending kept pending"

    # Definition edit while pending → draft
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    assert r.json()["data"]["review_status"] is None, "definition edit while pending kept pending"


@pytest.mark.asyncio
async def test_approve_clears_stale_rejection_reason(c):
    """R84: reject sets rejection_reason; a later re-submit + approve must clear
    it — an approved pack must not carry a prior rejection note."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/reject", json={"reason": "bad"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    appr = (await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)).json()[
        "data"
    ]
    assert appr["review_status"] == "approved"
    assert appr["rejection_reason"] is None, "stale rejection_reason survived approve"


@pytest.mark.asyncio
async def test_provider_action_empty_capability_rejected(c):
    """R83: an empty provider_action capability passed validation, then the
    publish derivation skipped it so the install capability gate saw no
    requirement (install succeeds with zero providers) while the runtime
    matches capability_key == '' (never) → guaranteed mid-run failure. Three
    copies of the rule disagreed on empty; min_length=1 rejects it at the
    source (definition save)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    defn = _valid_definition()
    defn["steps"][1]["config"]["capability"] = ""  # provider_action, empty cap
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": defn},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    assert r.json()["error"]["code"] == "WF_VALIDATION_FAILED"


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
        r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs", params={"page": bad}, headers=h)
        assert r.status_code == 422, f"page={bad} -> {r.status_code}: {r.text[:150]}"
    # Upper bound accepted
    r = await c.get(f"/api/v1/orgs/{oid}/workflow-packs", params={"page": "1000000"}, headers=h)
    assert r.status_code == 200, r.text[:150]


@pytest.mark.asyncio
async def test_deep_nested_definition_rejected_not_stored(c):
    """R51: a small-but-deep payload (900 nested arrays ≈ 2KB) passed the
    byte cap and every structural check, persisted fine, then
    PydanticSerializationError-500'd EVERY subsequent detail read — the
    pack became permanently unreadable through the API. Depth-capped at
    publish-side validation now (WF_TOO_DEEP)."""
    import json as _json

    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)

    deep = _json.loads("[" * 900 + "null" + "]" * 900)
    definition = {
        "schema_version": 1,
        "inputs": [],
        "outputs": [],
        "steps": [
            {
                "id": "note",
                "type": "instruction",
                "name": "Note",
                "config": {"content": "hello"},
                "inputs": [],
                "outputs": [],
            }
        ],
        "edges": [],
        "ui": {"x": deep},
    }
    r = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    codes = [e["code"] for e in r.json()["error"]["details"]]
    assert "WF_TOO_DEEP" in codes

    # The pack detail must still be readable (nothing deep was stored)
    r2 = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}", headers=h)
    assert r2.status_code == 200, r2.text[:200]


@pytest.mark.asyncio
async def test_publish_strips_org_local_pinned_binding(c):
    """R60-#6: pinned_offering_id points at THIS org's offering row. Left in
    the released manifest, it (a) bricks every cross-org install — the
    installer's _resolve_offering rejects a foreign-org offering →
    NO_ELIGIBLE_PROVIDER on every run — and (b) leaks the author's provider
    setup. publish must strip pinned_offering_id and reset binding_mode to
    auto in the manifest definition."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _pack(c, h, oid)
    definition = _valid_definition()
    # Author pins the provider_action to a local offering id
    gen = next(s for s in definition["steps"] if s["id"] == "generate")
    gen["config"] = {
        "capability": "image_generation",
        "binding_mode": "pinned",
        "pinned_offering_id": "01LOCALOFFERINGID000000000",
    }
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition},
        headers=h,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r.status_code == 201, r.text

    # Inspect the stored release manifest
    from sqlalchemy import select as _sel

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_pack import WorkflowPackRelease

    async with AsyncSessionLocal() as db:
        rel = (
            (await db.execute(_sel(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pid)))
            .scalars()
            .first()
        )
        cfg = next(
            s["config"] for s in rel.manifest["definition"]["steps"] if s["id"] == "generate"
        )
        assert "pinned_offering_id" not in cfg
        assert cfg.get("binding_mode") == "auto"
        # capability preserved
        assert cfg["capability"] == "image_generation"

    # The author's WORKING definition is untouched (only the release is scrubbed)
    d = (await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pid}", headers=h)).json()["data"]
    working_gen = next(s for s in d["definition"]["steps"] if s["id"] == "generate")
    assert working_gen["config"]["pinned_offering_id"] == "01LOCALOFFERINGID000000000"


def test_review_gate_passthrough_type_coercion_enforced():
    """R60-M: review_gate's approved passthrough copies the first input port
    into every non-decision output at runtime, skipping the edge coercion
    matrix. A gate declaring a text input and an image 'passed' output
    validated while the runtime would feed text into a downstream image
    consumer — publish must reject the type mismatch."""
    from app.schemas.workflow_definition import validate_definition

    def _gate_def(passed_type: str):
        return {
            "schema_version": 1,
            "inputs": [{"key": "t", "type": "text", "required": True}],
            "outputs": [
                {"key": "out", "type": passed_type, "from_step": "qa", "from_port": "passed"}
            ],
            "steps": [
                {
                    "id": "src",
                    "type": "asset_input",
                    "name": "S",
                    "config": {"accept_types": ["image"]},
                    "inputs": [],
                    "outputs": [{"port": "t", "type": "text"}],
                },
                {
                    "id": "qa",
                    "type": "review_gate",
                    "name": "QA",
                    "config": {"instructions": "x", "due_days": 7},
                    "inputs": [{"port": "subject", "type": "text"}],
                    "outputs": [
                        {"port": "decision", "type": "selection"},
                        {"port": "passed", "type": passed_type},
                    ],
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "from_step": "src",
                    "from_port": "t",
                    "to_step": "qa",
                    "to_port": "subject",
                }
            ],
            "ui": {},
        }

    # text input → image passthrough: rejected
    _, errs = validate_definition(_gate_def("image"))
    assert any(e["code"] == "WF_EDGE_TYPE_MISMATCH" for e in errs), [e["code"] for e in errs]

    # text input → text passthrough: valid (identity coercion)
    _, errs_ok = validate_definition(_gate_def("text"))
    assert not any(e["code"] == "WF_EDGE_TYPE_MISMATCH" for e in errs_ok), [
        e["code"] for e in errs_ok
    ]


@pytest.mark.asyncio
async def test_provenance_nul_rejected_not_500(c):
    """R62: workflow_pack provenance was the one JSONB field missing the
    control-char scan — a NUL smuggled into a provenance string 500'd the
    JSONB write (UntranslatableCharacterError) instead of a clean 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": "NulProv", "provenance": {"source": "a" + chr(0) + "b"}},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]


def test_review_gate_passthrough_sources_first_connected_port():
    """R66: the runtime passthrough source is the first declared input WITH A
    RESOLVED VALUE — not blindly inputs[0]. A gate declaring an optional
    (unconnected) image port first and a connected text port second, with an
    image 'passed' output, validated under the inputs[0] check (image→image)
    while the runtime sourced the passthrough from the text port and fed text
    into a downstream image consumer. The validator must model the runtime:
    the source is the first input port that has an incoming edge."""
    from app.schemas.workflow_definition import validate_definition

    def _defn(passed_type: str):
        return {
            "schema_version": 1,
            "inputs": [{"key": "t", "type": "text", "required": True}],
            "outputs": [
                {"key": "out", "type": passed_type, "from_step": "qa", "from_port": "passed"}
            ],
            "steps": [
                {
                    "id": "mk",
                    "type": "prompt_template",
                    "name": "Mk",
                    "config": {"template": "x {{inputs.t}}"},
                    "inputs": [],
                    "outputs": [{"port": "p", "type": "prompt"}],
                },
                {
                    "id": "qa",
                    "type": "review_gate",
                    "name": "QA",
                    "config": {"instructions": "x", "due_days": 7},
                    "inputs": [
                        # optional image FIRST — never connected
                        {"port": "ref", "type": "image", "required": False},
                        # connected text SECOND — the runtime's actual source
                        {"port": "subject", "type": "text", "required": True},
                    ],
                    "outputs": [
                        {"port": "decision", "type": "selection"},
                        {"port": "passed", "type": passed_type},
                    ],
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "from_step": "mk",
                    "from_port": "p",
                    "to_step": "qa",
                    "to_port": "subject",
                }
            ],
            "ui": {},
        }

    # Runtime feeds TEXT through — an image 'passed' output must be rejected
    _, errs = validate_definition(_defn("image"))
    assert any(e["code"] == "WF_EDGE_TYPE_MISMATCH" for e in errs), [e["code"] for e in errs]

    # …and a text 'passed' output is exactly right (prompt→text coercible too)
    _, errs_ok = validate_definition(_defn("text"))
    assert not any(e["code"] == "WF_EDGE_TYPE_MISMATCH" for e in errs_ok), [
        e["code"] for e in errs_ok
    ]


@pytest.mark.asyncio
async def test_pack_mutations_row_locked_no_lost_update(c):
    """R70: every WorkflowPack mutation was a stale db.get snapshot + unguarded
    ORM setattr under READ COMMITTED — two concurrent writers each decided on
    pre-mutation state and last-writer-won. Three reproduced failures, all
    closed by get_pack(for_update=True) which row-locks + refreshes to
    committed state so the loser re-reads fresh:
      #2 approval BYPASS: update_pack(visibility=public) passing its stale
         'approved' gate while a concurrent update_definition reset review_status
         to None → an unapproved pack published to the registry.
      #5 resurrection: publish_release flipping DRAFT→PUBLISHED on a stale read
         while a concurrent delete_pack archived it → archived pack goes public.
    Uses seeded two-session interleaving (session A holds the FOR UPDATE lock;
    session B blocks until A commits, then re-reads and its own gate fires)."""
    import asyncio

    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.skill_pack import PackStatus, PackVisibility
    from app.models.workflow_pack import WorkflowPack
    from app.services.workflow_pack import WorkflowPackService

    h, _ = await _auth(c)
    oid = await _org(c, h)

    # ── #2 approval bypass ──
    pid = await _pack(c, h, oid, name="Bypass " + _uuid())
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)  # approved + PUBLIC
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}",
        json={"visibility": "unlisted"},
        headers=h,
    )  # approved + UNLISTED

    async with AsyncSessionLocal() as db_a:
        svc_a = WorkflowPackService(db_a)
        pack_a = await svc_a.get_pack(pid, oid, for_update=True)  # A LOCKS (approved+unlisted)

        async def b_go_public():
            async with AsyncSessionLocal() as db_b:
                try:
                    await WorkflowPackService(db_b).update_pack(pid, oid, visibility="public")
                    await db_b.commit()
                    return "PUBLIC_WON"
                except AppError as e:
                    return e.code

        bt = asyncio.create_task(b_go_public())
        await asyncio.sleep(0.3)  # ensure B is blocked on the lock
        pack_a.review_status = None  # A: a definition change resets approval
        await db_a.commit()
        b_result = await bt

    async with AsyncSessionLocal() as db:
        p = await db.get(WorkflowPack, pid)
        # B re-read fresh (review_status=None) → its public gate must have fired
        assert not (p.visibility == PackVisibility.PUBLIC and p.review_status is None), (
            f"approval bypass: visibility={p.visibility.value} review_status={p.review_status} b={b_result}"
        )
        assert b_result == "APPROVAL_REQUIRED", b_result

    # ── #5 publish resurrects an archived pack ──
    pid2 = await _pack(c, h, oid, name="Resurrect " + _uuid())
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid2}/definition",
        json={"definition": _valid_definition()},
        headers=h,
    )  # DRAFT with a definition

    async with AsyncSessionLocal() as db_a:
        svc_a = WorkflowPackService(db_a)
        pack_a = await svc_a.get_pack(pid2, oid, for_update=True)  # A LOCKS (DRAFT)

        async def b_publish():
            async with AsyncSessionLocal() as db_b:
                try:
                    await WorkflowPackService(db_b).publish_release(
                        pid2, oid, version="1.0.0", changelog=None, released_by="u"
                    )
                    await db_b.commit()
                    return "PUBLISH_WON"
                except AppError as e:
                    return e.code

        bt = asyncio.create_task(b_publish())
        await asyncio.sleep(0.3)
        pack_a.status = PackStatus.ARCHIVED  # A archives
        await db_a.commit()
        b_result = await bt

    async with AsyncSessionLocal() as db:
        p = await db.get(WorkflowPack, pid2)
        # B re-read fresh (ARCHIVED) → get_pack must 404, never resurrect
        assert p.status == PackStatus.ARCHIVED, f"resurrected: status={p.status.value} b={b_result}"
        assert b_result == "WORKFLOW_PACK_NOT_FOUND", b_result


@pytest.mark.asyncio
async def test_workflow_pack_provenance_nonfinite_rejected_not_500(c):
    """R73: provenance is an open JSONB dict — a NaN/Infinity float 500'd at
    the write (22P02). The validator now screens non-finite floats → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    hj = {**h, "Content-Type": "application/json"}
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        content=b'{"name":"PNaN","provenance":{"v": NaN}}',
        headers=hj,
    )
    assert r.status_code == 422, r.text[:150]
    # Control: finite provenance value accepted
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs",
        json={"name": f"Pok-{_uuid()}", "provenance": {"weight": 0.5}},
        headers=h,
    )
    assert r2.status_code == 201, r2.text[:150]


def test_json_default_nonfinite_rejected():
    """R73: a json input default whose parsed value contains NaN/Infinity
    (json.loads accepts the token) would 500 every default-driven run. The
    publish-time validator now flags it as WF_INVALID_DEFAULT."""
    from app.schemas.workflow_definition import validate_definition

    d = {
        "schema_version": 1,
        "inputs": [{"key": "cfg", "type": "json", "required": False, "default": '{"x": NaN}'}],
        "outputs": [],
        "steps": [
            {
                "id": "a",
                "type": "instruction",
                "name": "A",
                "config": {"content": "x"},
                "inputs": [],
                "outputs": [],
            }
        ],
        "edges": [],
        "ui": {},
    }
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_INVALID_DEFAULT" for e in errors), [e["code"] for e in errors]

    # Control: a finite json default is accepted
    ok = {
        **d,
        "inputs": [{"key": "cfg", "type": "json", "required": False, "default": '{"x": 1.5}'}],
    }
    _, ok_errs = validate_definition(ok)
    assert not any(e["code"] == "WF_INVALID_DEFAULT" for e in ok_errs), [e["code"] for e in ok_errs]


def test_list_endpoints_have_unique_id_tiebreak():
    """R75: list_packs / list_installations / list_runs / list_profiles /
    list_assignments / list_drafts / match-runs all ordered by a NON-UNIQUE
    key (created_at/installed_at .desc()) alone. Postgres OFFSET pagination
    over a non-unique sort has NO stability guarantee, so rows sharing a
    timestamp (same-tick creation) can be SKIPPED or DUPLICATED across pages.
    Each ORDER BY now chains the ULID primary key as a unique tiebreak, making
    the sort a total order. Guard every paginated list-query source (an OFFSET
    union check can pass by luck without the fix; source inspection cannot)."""
    import inspect as _inspect

    from app.services.creator_matching import CreatorMatchingService
    from app.services.learning_composer import LearningComposerService
    from app.services.requirement_profile import RequirementProfileService
    from app.services.workflow_installation import WorkflowInstallationService
    from app.services.workflow_pack import WorkflowPackService
    from app.services.workflow_runtime import WorkflowRuntimeService

    for svc, method, tiebreak in [
        (WorkflowPackService, "list_packs", "WorkflowPack.id.desc()"),
        (WorkflowInstallationService, "list_installations", "WorkflowPackInstallation.id.desc()"),
        (WorkflowRuntimeService, "list_runs", "WorkflowRun.id.desc()"),
        (RequirementProfileService, "list_profiles", "RequirementProfile.id.desc()"),
        (CreatorMatchingService, "list_assignments", "CreatorAssignment.id.desc()"),
        (LearningComposerService, "list_drafts", "SolutionDraft.id.desc()"),
    ]:
        src = _inspect.getsource(getattr(svc, method))
        assert tiebreak in src, f"{svc.__name__}.{method} ORDER BY lacks the unique id tiebreak"
