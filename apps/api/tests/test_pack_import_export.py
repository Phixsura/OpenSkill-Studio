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
    r = await c.post("/api/v1/orgs", json={"name": f"IO-{uuid.uuid4().hex[:6]}"}, headers=h)
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
