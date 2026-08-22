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
