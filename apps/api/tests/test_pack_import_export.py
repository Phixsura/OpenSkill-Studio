"""Integration tests for pack import/export — round-trip, security guards."""

import io
import json
import uuid
import zipfile

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"io-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "IO"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


def _make_zip(manifest: dict, extra_files: dict | None = None) -> bytes:
    """Create a zip in memory with the given manifest."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("openskill-pack.json", json.dumps(manifest))
        if extra_files:
            for name, content in extra_files.items():
                zf.writestr(name, content)
    buf.seek(0)
    return buf.getvalue()


VALID_MANIFEST = {
    "schema_version": "1",
    "pack": {
        "name": "Test Import Pack",
        "summary": "A test pack",
        "metadata": {"difficulty": "beginner", "scenario_tags": ["test"]},
        "provenance": {"author_name": "Test Author"},
    },
    "categories": [{"logical_id": "cat-1", "name": "Basics", "slug": "basics", "sort_order": 0}],
    "skills": [
        {
            "logical_id": "skill-1",
            "category_logical_id": "cat-1",
            "name": "Test Skill",
            "slug": "test-skill",
            "description": "A test skill",
            "difficulty": "beginner",
            "sort_order": 0,
            "exercises": [
                {
                    "logical_id": "skill-1/ex-1",
                    "title": "Test Exercise",
                    "description": "A test exercise",
                    "type": "text_answer",
                    "config": {},
                    "max_score": 100,
                    "sort_order": 0,
                }
            ],
            "prerequisites": [],
        }
    ],
    "project_templates": [
        {
            "logical_id": "tmpl-1",
            "name": "Test Template",
            "description": "A test template",
            "instructions": "Instructions",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
            "sort_order": 0,
        }
    ],
}


@pytest.mark.asyncio
async def test_import_valid_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    zip_bytes = _make_zip(VALID_MANIFEST)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
        headers=h,
    )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["pack"]["name"] == "Test Import Pack"
    assert data["release"]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_import_missing_manifest(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", "no manifest here")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "manifest" in r.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_import_invalid_schema_version(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {**VALID_MANIFEST, "schema_version": "999"}
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "schema" in r.json()["error"]["code"].lower()


@pytest.mark.asyncio
async def test_import_duplicate_logical_ids(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        **VALID_MANIFEST,
        "skills": [
            {**VALID_MANIFEST["skills"][0], "logical_id": "dup"},
            {**VALID_MANIFEST["skills"][0], "logical_id": "dup"},
        ],
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "DUPLICATE" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_invalid_prerequisite(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        **VALID_MANIFEST,
        "skills": [{**VALID_MANIFEST["skills"][0], "prerequisites": ["nonexistent"]}],
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "PREREQUISITE" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_path_traversal(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        zf.writestr("../../../etc/passwd", "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_not_a_zip(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.txt", b"not a zip file", "text/plain")},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_export_round_trip(c):
    """Export a release, then import it into another org."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    # Create pack + publish in org1
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "Round Trip"}, headers=h1)).json()["data"]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "RT"}, headers=h1)).json()["data"]["id"]
    sid = (await c.post(f"/api/v1/orgs/{oid1}/skills", json={
        "name": "RT Skill", "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h1)).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    # Export
    r = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}/releases/1.0.0/export", headers=h1)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"

    # Import into org2
    r2 = await c.post(
        f"/api/v1/orgs/{oid2}/packs/import",
        files={"file": ("pack.zip", r.content, "application/zip")},
        headers=h2,
    )
    assert r2.status_code == 201
    assert r2.json()["data"]["pack"]["name"] == "Round Trip"


# ═══════════════ Import Security ═══════════════


@pytest.mark.asyncio
async def test_import_malicious_backslash_path(c):
    """Zip entry with backslash path triggers MALICIOUS_ARCHIVE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        zf.writestr("assets\\..\\etc\\passwd", "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_malicious_absolute_path(c):
    """Zip entry with absolute path triggers MALICIOUS_ARCHIVE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        info = zipfile.ZipInfo("/root/secret.txt")
        info.filename = "/root/secret.txt"
        zf.writestr(info, "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_malformed_json_manifest(c):
    """Manifest with invalid JSON triggers INVALID_MANIFEST."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", "not json {{{")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_missing_pack_name(c):
    """Manifest without pack.name triggers INVALID_MANIFEST."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {"schema_version": "1", "pack": {"summary": "No name here"}}
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_missing_skills_field(c):
    """Manifest without skills or templates should be rejected as empty."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        "schema_version": "1",
        "pack": {"name": "No Skills Pack", "summary": "A pack with no skills"},
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("pack.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EMPTY_MANIFEST"


@pytest.mark.asyncio
async def test_import_too_many_files(c):
    """Zip with >500 entries triggers TOO_MANY_FILES."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        for i in range(500):
            zf.writestr(f"file_{i}.txt", "x")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("big.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "TOO_MANY_FILES"


@pytest.mark.asyncio
async def test_import_preserves_metadata(c):
    """Import preserves scenario_tags, tool_tags, and capability_tags."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        **VALID_MANIFEST,
        "pack": {
            **VALID_MANIFEST["pack"],
            "metadata": {
                "difficulty": "intermediate",
                "scenario_tags": ["ecommerce", "saas"],
                "tool_tags": ["comfyui", "blender"],
                "capability_tags": ["texturing", "lighting"],
            },
        },
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("meta.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 201
    pack = r.json()["data"]["pack"]
    assert pack["difficulty"] == "intermediate"
    assert pack["scenario_tags"] == ["ecommerce", "saas"]
    assert pack["tool_tags"] == ["comfyui", "blender"]
    assert pack["capability_tags"] == ["texturing", "lighting"]


@pytest.mark.asyncio
async def test_import_duplicate_template_logical_ids(c):
    """Two templates with the same logical_id triggers DUPLICATE_LOGICAL_ID."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    template = VALID_MANIFEST["project_templates"][0]
    manifest = {
        **VALID_MANIFEST,
        "project_templates": [
            {**template, "logical_id": "tmpl-dup"},
            {**template, "logical_id": "tmpl-dup"},
        ],
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "DUPLICATE" in r.json()["error"]["code"]


# ═══════════════ Export ═══════════════


@pytest.mark.asyncio
async def test_export_release_not_found(c):
    """Export of non-existent version returns 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "No Release"}, headers=h)
    ).json()["data"]["id"]

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/9.9.9/export", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_export_zip_contains_valid_manifest(c):
    """Exported zip contains openskill-pack.json with valid JSON and schema_version."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "Manifest Check"}, headers=h)
    ).json()["data"]["id"]
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "MC"}, headers=h)
    ).json()["data"]["id"]
    sid = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "MC Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/1.0.0/export", headers=h)
    assert r.status_code == 200

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    assert "openskill-pack.json" in zf.namelist()
    manifest = json.loads(zf.read("openskill-pack.json"))
    assert manifest["schema_version"] == "1"


@pytest.mark.asyncio
async def test_export_filename_format(c):
    """Content-Disposition header contains pack name slug and version."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(f"/api/v1/orgs/{oid}/packs", json={"name": "My Export Pack"}, headers=h)
    ).json()["data"]["id"]
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "EF"}, headers=h)
    ).json()["data"]["id"]
    sid = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "EF Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "2.0.0"}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/releases/2.0.0/export", headers=h)
    assert r.status_code == 200
    cd = r.headers["content-disposition"]
    assert "my-export-pack" in cd
    assert "2.0.0" in cd
    assert ".zip" in cd


@pytest.mark.asyncio
async def test_export_cross_org(c):
    """Org2 cannot export org1's pack release."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    _oid2 = await _org(c, h2)

    pid = (
        await c.post(f"/api/v1/orgs/{oid1}/packs", json={"name": "Cross Export"}, headers=h1)
    ).json()["data"]["id"]
    cat = (
        await c.post(f"/api/v1/orgs/{oid1}/categories", json={"name": "CE"}, headers=h1)
    ).json()["data"]["id"]
    sid = (
        await c.post(
            f"/api/v1/orgs/{oid1}/skills",
            json={
                "name": "CE Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h1,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h1)

    # Org2 tries to export from org1's namespace
    r = await c.get(f"/api/v1/orgs/{oid1}/packs/{pid}/releases/1.0.0/export", headers=h2)
    assert r.status_code in (403, 404)


# ═══════════════ Import Security — /etc/ and /dev/ paths ═══════════════


@pytest.mark.asyncio
async def test_import_malicious_etc_path(c):
    """Zip entry containing '/etc/' triggers MALICIOUS_ARCHIVE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        zf.writestr("assets/etc/shadow", "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


@pytest.mark.asyncio
async def test_import_malicious_dev_path(c):
    """Zip entry containing '/dev/' triggers MALICIOUS_ARCHIVE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        zf.writestr("assets/dev/null", "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


# ═══════════════ Import Validation — missing logical_id ═══════════════


@pytest.mark.asyncio
async def test_import_skill_missing_logical_id(c):
    """Skill without logical_id triggers INVALID_MANIFEST."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        **VALID_MANIFEST,
        "skills": [{
            "name": "No LID Skill",
            "category_logical_id": "cat-1",
            "description": "test",
            "difficulty": "beginner",
            "sort_order": 0,
            "exercises": [],
            "prerequisites": [],
        }],
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_template_missing_logical_id(c):
    """Template without logical_id triggers INVALID_MANIFEST."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        **VALID_MANIFEST,
        "project_templates": [{
            "name": "No LID Template",
            "description": "test",
            "instructions": "do it",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "sort_order": 0,
        }],
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


# ═══════════════ /proc path ═══════════════


@pytest.mark.asyncio
async def test_import_malicious_proc_path(c):
    """Zip entry with '/proc/self/environ' triggers MALICIOUS_ARCHIVE."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", json.dumps(VALID_MANIFEST))
        info = zipfile.ZipInfo("/proc/self/environ")
        info.filename = "/proc/self/environ"
        zf.writestr(info, "malicious")
    buf.seek(0)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "MALICIOUS" in r.json()["error"]["code"]


# ═══════════════ Missing schema_version ═══════════════


@pytest.mark.asyncio
async def test_import_missing_schema_version(c):
    """Manifest without schema_version key → 422 UNSUPPORTED_SCHEMA."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    manifest = {
        "pack": {
            "name": "No Schema Version",
            "summary": "Missing schema_version",
        },
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("bad.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422
    assert "SCHEMA" in r.json()["error"]["code"].upper()


# ═══════════════ Student cannot import ═══════════════


@pytest.mark.asyncio
async def test_import_student_cannot_import(c):
    """Student role cannot import a pack → 403."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h)

    zip_bytes = _make_zip(VALID_MANIFEST)
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
        headers=hs,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_import_deep_manifest_rejected(c):
    """R56: a deep-nested manifest (400 levels ≈ 2KB) previously either
    RecursionError-500'd at the canonical json.dumps, or — smuggled inside
    pack.provenance — stored verbatim and bricked every pack read
    (provenance is echoed by SkillPackResponse). Clean 422 now."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)

    deep = json.loads("[" * 400 + "null" + "]" * 400)
    manifest = copy.deepcopy(VALID_MANIFEST)
    manifest["pack"]["provenance"] = {"x": deep}
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("deep.zip", _make_zip(manifest), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"

    # Direct create/update schema paths also reject deep provenance
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/packs",
        json={"name": "DeepProvSkill", "provenance": {"x": deep}},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]


@pytest.mark.asyncio
async def test_import_malformed_manifest_types_rejected_not_500(c):
    """R62: wrong-typed manifest JSON must be a clean 422, not an
    AttributeError/TypeError 500 deep in create_pack (the import path trusts
    the manifest structure)."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)

    bad_pack = copy.deepcopy(VALID_MANIFEST)
    bad_pack["pack"] = ["not", "an", "object"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(bad_pack), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]

    bad_skills = copy.deepcopy(VALID_MANIFEST)
    bad_skills["skills"] = ["skill1", "skill2"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(bad_skills), "application/zip")},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]

    bad_name = copy.deepcopy(VALID_MANIFEST)
    bad_name["pack"]["name"] = 12345
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(bad_name), "application/zip")},
        headers=h,
    )
    assert r3.status_code == 422, r3.text[:200]


@pytest.mark.asyncio
async def test_import_overlong_manifest_strings_rejected(c):
    """R62: manifest name/version flow into capped VARCHAR columns; an
    over-length value must 422, not StringDataRightTruncation 500."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)

    long_name = copy.deepcopy(VALID_MANIFEST)
    long_name["pack"]["name"] = "x" * 500
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(long_name), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]

    long_ver = copy.deepcopy(VALID_MANIFEST)
    long_ver["version"] = "1.0.0-" + "a" * 200
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(long_ver), "application/zip")},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]


@pytest.mark.asyncio
async def test_import_nul_in_manifest_rejected(c):
    """R62: a NUL smuggled into a manifest string (valid JSON escape) must
    422, not crash the JSONB/text write with UntranslatableCharacterError."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)
    m = copy.deepcopy(VALID_MANIFEST)
    m["pack"]["summary"] = "a" + chr(0) + "b"
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(m), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_hostile_entry_types_rejected_not_500(c):
    """R65: per-entry structural typing. Unhashable/wrong-typed values in
    skills entries, exercises, metadata, and provenance turned into
    TypeError/AttributeError 500s (10 live-confirmed cases), and an int
    logical_id sailed through to a 201 with a non-string id in the published
    manifest. Every hostile case must be a clean 422 INVALID_MANIFEST."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)

    def variant(mutate):
        m = copy.deepcopy(VALID_MANIFEST)
        mutate(m)
        return m

    def set_meta(m, key, value):
        m["pack"].setdefault("metadata", {})[key] = value

    cases = {
        "prereq unhashable": variant(
            lambda m: m["skills"][0].__setitem__("prerequisites", [["x"]])
        ),
        "prereq int": variant(
            lambda m: m["skills"][0].__setitem__("prerequisites", [1])
        ),
        "prereqs str": variant(
            lambda m: m["skills"][0].__setitem__("prerequisites", "a")
        ),
        "exercises str": variant(
            lambda m: m["skills"][0].__setitem__("exercises", "zzz")
        ),
        "exercise item str": variant(
            lambda m: m["skills"][0].__setitem__("exercises", ["x"])
        ),
        "logical_id list": variant(
            lambda m: m["skills"][0].__setitem__("logical_id", ["a"])
        ),
        "logical_id int": variant(
            lambda m: m["skills"][0].__setitem__("logical_id", 7)
        ),
        "learning_content int": variant(
            lambda m: m["skills"][0].__setitem__("learning_content", 12345)
        ),
        # R78: falsy non-strings bypassed the gate via `lc and ...` truthiness
        "learning_content zero": variant(
            lambda m: m["skills"][0].__setitem__("learning_content", 0)
        ),
        "learning_content false": variant(
            lambda m: m["skills"][0].__setitem__("learning_content", False)
        ),
        "learning_content empty list": variant(
            lambda m: m["skills"][0].__setitem__("learning_content", [])
        ),
        "exercise config str": variant(
            lambda m: m["skills"][0].__setitem__(
                "exercises",
                [{"logical_id": "e1", "type": "multiple_choice", "config": "zz"}],
            )
        ),
        "exercise logical_id dict": variant(
            lambda m: m["skills"][0].__setitem__(
                "exercises", [{"logical_id": {"x": 1}, "type": "text_answer"}]
            )
        ),
        "est_minutes str": variant(lambda m: set_meta(m, "estimated_minutes", "NaN")),
        "est_minutes bool": variant(lambda m: set_meta(m, "estimated_minutes", True)),
        "outcomes dict": variant(
            lambda m: set_meta(m, "learning_outcomes", {"x": 1})
        ),
        "tags int": variant(lambda m: set_meta(m, "scenario_tags", 7)),
        "provenance list": variant(
            lambda m: m["pack"].__setitem__("provenance", ["x"])
        ),
        "metadata str": variant(lambda m: m["pack"].__setitem__("metadata", "zz")),
    }
    for name, manifest in cases.items():
        r = await c.post(
            f"/api/v1/orgs/{oid}/packs/import",
            files={"file": ("m.zip", _make_zip(manifest), "application/zip")},
            headers=h,
        )
        assert r.status_code == 422, f"{name}: {r.status_code} {r.text[:150]}"
        assert r.json()["error"]["code"] in ("INVALID_MANIFEST",), name

    # Control: the unmodified valid manifest still imports
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(VALID_MANIFEST), "application/zip")},
        headers=h,
    )
    assert r.status_code == 201, r.text[:200]


@pytest.mark.asyncio
async def test_import_accepts_platform_composed_exercise_logical_id(c):
    """R78: the export path composes exercise logical_ids as
    f"{skill.slug}/{title_slug[:50]}" — slug is legitimately up to 200 chars,
    so the composed id reaches 251. R65's gate capped it at 200, rejecting the
    platform's OWN export→import roundtrip for long-slugged skills. The cap is
    now 251; anything longer stays a clean 422."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)

    slug = "a" * 200
    composed = f"{slug}/{'b' * 50}"  # 251 chars — exactly what export produces
    m = copy.deepcopy(VALID_MANIFEST)
    m["skills"][0]["logical_id"] = slug
    m["skills"][0]["slug"] = slug
    m["skills"][0]["exercises"] = [
        {
            "logical_id": composed,
            "title": "b" * 60,
            "description": "d",
            "type": "text_answer",
            "config": {},
            "max_score": 100,
            "sort_order": 0,
        }
    ]
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(m), "application/zip")},
        headers=h,
    )
    assert r.status_code == 201, f"{r.status_code}: {r.text[:250]}"

    # 252+ chars is beyond anything the platform composes — still rejected
    m2 = copy.deepcopy(m)
    m2["skills"][0]["exercises"][0]["logical_id"] = composed + "x"
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", _make_zip(m2), "application/zip")},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]
    assert r2.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_bigint_literal_rejected_not_500(c):
    """R70: a JSON integer literal longer than CPython's 4300-digit int-string
    limit makes json.loads raise a BARE ValueError (not JSONDecodeError). The
    manifest parse only caught (JSONDecodeError, KeyError), so the ValueError
    escaped to a 500. Must be a clean 422 INVALID_MANIFEST."""
    import io
    import zipfile

    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Build the zip with a RAW json string (json.dumps would render the int
    # fine — the bug is only in PARSING the oversized literal back).
    raw = (
        '{"schema_version": "1", "version": "1.0.0", '
        '"pack": {"name": "P"}, "skills": [{"logical_id": "a"}], '
        '"n": ' + ("9" * 5000) + "}"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("openskill-pack.json", raw)

    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("m.zip", buf.getvalue(), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, f"{r.status_code}: {r.text[:200]}"
    assert r.json()["error"]["code"] == "INVALID_MANIFEST"


@pytest.mark.asyncio
async def test_import_nonfinite_float_rejected_not_500(c):
    """R86: json.loads accepts bare NaN/Infinity/-Infinity tokens and yields
    real float('nan')/float('inf'), which pass the NUL/type/size checks but the
    default JSONB serializer re-emits verbatim → Postgres 22P02 → 500 at the
    manifest insert. Must be a clean 422 INVALID_MANIFEST (parity with every
    other JSONB write surface, all of which screen non-finite)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for token in ("NaN", "Infinity", "-Infinity"):
        raw = (
            '{"schema_version": "1", "version": "1.0.0", '
            '"pack": {"name": "NF"}, "categories": [], '
            '"skills": [{"logical_id": "s1", "name": "S", "exercises": ['
            '{"logical_id": "s1/e1", "title": "E", "config": {"t": ' + token + "}}]}], "
            '"project_templates": []}'
        )
        assert token in raw
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("openskill-pack.json", raw)
        r = await c.post(
            f"/api/v1/orgs/{oid}/packs/import",
            files={"file": ("nf.zip", buf.getvalue(), "application/zip")},
            headers=h,
        )
        assert r.status_code == 422, f"{token}: {r.status_code} {r.text[:200]}"
        assert r.json()["error"]["code"] == "INVALID_MANIFEST", r.text[:200]


@pytest.mark.asyncio
async def test_import_dangling_category_ref_rejected_at_import(c):
    """R86: a skill's category_logical_id is resolved against manifest
    categories[] at INSTALL time (installation.py CATEGORY_NOT_FOUND). Import
    never validated it, so a dangling reference imported to PUBLISHED and then
    EVERY install failed — an unrecoverable published-but-uninstallable pack.
    The dangling reference must be a clean 422 at IMPORT time."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)
    m = copy.deepcopy(VALID_MANIFEST)
    m["categories"] = []  # define no categories...
    m["skills"][0]["category_logical_id"] = "ghost-cat"  # ...but reference one
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("cat.zip", _make_zip(m), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    assert r.json()["error"]["code"] == "INVALID_MANIFEST", r.text[:200]


@pytest.mark.asyncio
async def test_import_nonint_exercise_max_score_rejected_not_500(c):
    """R86: exercise max_score / sort_order (and skill sort_order) flow verbatim
    into INTEGER columns at INSTALL time with only .get(default). A non-int
    value imported to PUBLISHED and then crashed every install with a 500
    (DataError). Must be a clean 422 at import."""
    import copy

    h, _ = await _auth(c)
    oid = await _org(c, h)
    for field, bad in (
        ("max_score", "NOTANINT"),
        ("max_score", 3.5),
        ("sort_order", "x"),
    ):
        m = copy.deepcopy(VALID_MANIFEST)
        m["skills"][0]["exercises"][0][field] = bad
        r = await c.post(
            f"/api/v1/orgs/{oid}/packs/import",
            files={"file": ("ms.zip", _make_zip(m), "application/zip")},
            headers=h,
        )
        assert r.status_code == 422, f"{field}={bad!r}: {r.status_code} {r.text[:200]}"
        assert r.json()["error"]["code"] == "INVALID_MANIFEST", r.text[:200]

    # skill-level sort_order too
    m = copy.deepcopy(VALID_MANIFEST)
    m["skills"][0]["sort_order"] = "first"
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs/import",
        files={"file": ("ss.zip", _make_zip(m), "application/zip")},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
