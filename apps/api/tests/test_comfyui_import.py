"""Tests for safe ComfyUI import + sanitize module (ADR-010 D4 layer 4, D10)."""

import base64
import json
import struct
import uuid
import zlib
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
    return f"cui-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "CUI"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"C-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


def _ui_workflow() -> dict:
    """Small valid UI-format ComfyUI workflow."""
    return {
        "last_node_id": 5,
        "last_link_id": 4,
        "nodes": [
            {"id": 1, "type": "CheckpointLoaderSimple", "widgets_values": ["model.safetensors"]},
            {"id": 2, "type": "KSampler", "widgets_values": [42, "fixed", 20, 7.5]},
            {"id": 3, "type": "LoadImage", "widgets_values": ["input.png"]},
            {"id": 4, "type": "SaveImage", "widgets_values": ["output"]},
            {"id": 5, "type": "MyCustomNode", "title": "My custom", "widgets_values": []},
        ],
        "links": [[1, 1, 0, 2, 0, "MODEL"], [2, 3, 0, 2, 1, "IMAGE"]],
        "version": 0.4,
    }


def _api_workflow() -> dict:
    return {
        "1": {"class_type": "KSampler", "inputs": {"seed": 42, "model": ["2", 0]}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd15.ckpt"}},
    }


def _png_with_workflow(workflow_json: str) -> bytes:
    """Build a minimal valid PNG with a tEXt 'workflow' chunk."""

    def chunk(ctype: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + ctype
            + data
            + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        )

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0))
    text = chunk(b"tEXt", b"workflow\x00" + workflow_json.encode("latin-1"))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + text + iend


# ── Import formats ────────────────────────────────────────


@pytest.mark.asyncio
async def test_import_ui_format(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(_ui_workflow()), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["format_detected"] == "ui"
    assert data["status"] == "imported"
    report = data["dependency_report"]
    # Custom node detected
    assert any(cn["class_type"] == "MyCustomNode" for cn in report["custom_nodes"])
    assert report["custom_node_count"] == 1
    assert report["core_node_count"] == 4
    # Model with whitelist confidence (from CheckpointLoaderSimple)
    model = next(m for m in report["models"] if m["filename"] == "model.safetensors")
    assert model["confidence"] == "whitelist"
    # Capability detected via KSampler
    assert "image_generation" in report["capabilities_detected"]
    # I/O nodes
    assert "LoadImage" in report["input_nodes"]
    assert "SaveImage" in report["output_nodes"]
    assert len(data["original_sha256"]) == 64


@pytest.mark.asyncio
async def test_import_api_format(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(_api_workflow()), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["format_detected"] == "api"
    report = data["dependency_report"]
    assert report["total_nodes"] == 2
    # sd15.ckpt found via API inputs scan
    assert any(m["filename"] == "sd15.ckpt" for m in report["models"])
    assert "image_generation" in report["capabilities_detected"]


@pytest.mark.asyncio
async def test_import_png_embedded(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    png = _png_with_workflow(json.dumps(_api_workflow()))
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": base64.b64encode(png).decode(), "encoding": "base64"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["format_detected"] == "png_embedded"
    assert data["dependency_report"]["total_nodes"] == 2


@pytest.mark.asyncio
async def test_png_without_workflow_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    def chunk(ctype: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + ctype
            + data
            + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0))
        + chunk(b"IEND", b"")
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": base64.b64encode(png).decode(), "encoding": "base64"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "NO_WORKFLOW_IN_PNG"


# ── Rejection paths ───────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_json_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": "{not json", "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_JSON"


@pytest.mark.asyncio
async def test_unrecognized_format_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps({"foo": "bar"}), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "UNRECOGNIZED_FORMAT"


@pytest.mark.asyncio
async def test_too_many_nodes_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    big = {str(i): {"class_type": "KSampler", "inputs": {}} for i in range(2001)}
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(big), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "IMPORT_TOO_COMPLEX"


@pytest.mark.asyncio
async def test_oversized_import_rejected(c):
    """Service-level 5MB cap (schema allows up to 7MB string)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    filler = "x" * (6 * 1024 * 1024)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": filler, "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "IMPORT_TOO_LARGE"


@pytest.mark.asyncio
async def test_invalid_base64_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": "!!!not-base64!!!", "encoding": "base64"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_BASE64"


# ── Sanitization of untrusted node titles ─────────────────


@pytest.mark.asyncio
async def test_node_title_sanitized_in_report(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    wf = _ui_workflow()
    # Custom node with hostile class type containing invisible + control chars
    wf["nodes"].append(
        {
            "id": 6,
            "type": "Evil​Node\x07Name",  # zero-width + bell
            "title": "inject‮me",  # bidi override
            "widgets_values": [],
        }
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(wf), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 201
    report = r.json()["data"]["dependency_report"]
    evil = next(cn for cn in report["custom_nodes"] if "Evil" in cn["class_type"])
    assert evil["class_type"] == "EvilNodeName"  # invisible + control chars stripped


# ── Draft pack creation ───────────────────────────────────


@pytest.mark.asyncio
async def test_create_pack_from_import(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(_ui_workflow()), "encoding": "json"},
        headers=h,
    )
    import_id = r.json()["data"]["id"]

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports/{import_id}/create-pack",
        json={"name": "Imported Hero Workflow"},
        headers=h,
    )
    assert r2.status_code == 201, r2.text
    pack = r2.json()["data"]
    assert pack["status"] == "draft"
    assert pack["provenance"]["source"] == "comfyui_import"
    assert pack["provenance"]["import_id"] == import_id

    # Pack definition has a provider_action for the detected capability +
    # an instruction step listing custom nodes
    r3 = await c.get(f"/api/v1/orgs/{oid}/workflow-packs/{pack['id']}", headers=h)
    definition = r3.json()["data"]["definition"]
    step_types = {s["id"]: s["type"] for s in definition["steps"]}
    assert step_types.get("comfy_image_generation") == "provider_action"
    assert step_types.get("comfy_unmapped") == "instruction"
    unmapped = next(s for s in definition["steps"] if s["id"] == "comfy_unmapped")
    assert "MyCustomNode" in unmapped["config"]["content"]

    # Import row updated
    r4 = await c.get(f"/api/v1/orgs/{oid}/comfyui-imports/{import_id}", headers=h)
    assert r4.json()["data"]["status"] == "mapped"
    assert r4.json()["data"]["pack_id"] == pack["id"]


# ── Access control / privacy ──────────────────────────────


@pytest.mark.asyncio
async def test_import_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/comfyui-imports",
        json={"data": json.dumps(_api_workflow()), "encoding": "json"},
        headers=h1,
    )
    import_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/comfyui-imports/{import_id}", headers=h2)
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_original_json_excluded_by_default(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(_api_workflow()), "encoding": "json"},
        headers=h,
    )
    import_id = r.json()["data"]["id"]

    r2 = await c.get(f"/api/v1/orgs/{oid}/comfyui-imports/{import_id}", headers=h)
    assert r2.json()["data"]["original_json"] is None

    r3 = await c.get(
        f"/api/v1/orgs/{oid}/comfyui-imports/{import_id}?include_original=true", headers=h
    )
    assert r3.json()["data"]["original_json"] is not None
    assert "1" in r3.json()["data"]["original_json"]


@pytest.mark.asyncio
async def test_student_cannot_import(c):
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    h_student, u_student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": u_student["id"], "role": "student"},
        headers=h_owner,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(_api_workflow()), "encoding": "json"},
        headers=h_student,
    )
    assert r.status_code == 403


# ── No-network guarantee ──────────────────────────────────


def test_import_service_has_no_network_io():
    """The import service must never make network calls (D4 layer 4)."""
    import pathlib

    source = pathlib.Path("app/services/comfyui_import.py").read_text()
    assert "httpx" not in source
    assert "aiohttp" not in source
    assert "urllib" not in source
    assert "requests" not in source
    assert "socket" not in source


# ── sanitize_untrusted_text unit tests (D10) ──────────────


def test_sanitize_strips_zero_width():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("a​b‌c‍d﻿e⁠f") == "abcdef"


def test_sanitize_strips_tags_block():
    from app.core.sanitize import sanitize_untrusted_text

    # ASCII smuggling via Unicode Tags block
    assert sanitize_untrusted_text("hello\U000E0041\U000E0042world") == "helloworld"


def test_sanitize_strips_bidi_controls():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("a‮b‪c⁦d⁩e") == "abcde"


def test_sanitize_strips_control_chars_keeps_newline_tab():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("a\x00b\x07c\x1bd") == "abcd"
    assert sanitize_untrusted_text("line1\nline2\tend") == "line1\nline2\tend"


def test_sanitize_nfkc_normalizes():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("ＡＢＣ") == "ABC"  # fullwidth → ASCII


def test_sanitize_truncates():
    from app.core.sanitize import sanitize_untrusted_text

    assert len(sanitize_untrusted_text("x" * 5000, 120)) == 120


def test_sanitize_empty_and_none_safe():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("") == ""
