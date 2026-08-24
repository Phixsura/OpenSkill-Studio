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


@pytest.mark.asyncio
async def test_create_pack_with_hostile_class_type(c):
    """A class_type containing moustache/data-URI syntax must not make the
    generated draft definition fail validation (audit fix)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    payload = {
        "1": {"class_type": "KSampler", "inputs": {}},
        "2": {"class_type": "{{inputs.x}}", "inputs": {}},
        "3": {"class_type": "data:text/html;base64,EvilNode", "inputs": {}},
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(payload), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    import_id = r.json()["data"]["id"]

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports/{import_id}/create-pack",
        json={"name": "Hostile Class Types"},
        headers=h,
    )
    assert r2.status_code == 201, r2.text


@pytest.mark.asyncio
async def test_deeply_nested_json_returns_422(c):
    """RecursionError from deeply nested JSON must be a 422, not a 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    deep = "[" * 50000 + "]" * 50000
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": deep, "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 422
    # INVALID_JSON (RecursionError path) or UNRECOGNIZED_FORMAT (if it parsed)
    assert r.json()["error"]["code"] in ("INVALID_JSON", "UNRECOGNIZED_FORMAT")


# ── Adversarial hardening (parser fuzz round) ─────────────


@pytest.mark.asyncio
async def test_scalar_widgets_values_no_crash(c):
    """widgets_values may be any JSON type in hostile input — scalars were
    kept by `or []` (truthy) and TypeError'd in the report loop (500)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for hostile in (5, True, 3.14, "model.safetensors", {"k.ckpt": 1}):
        payload = {"nodes": [{"type": "CheckpointLoaderSimple", "widgets_values": hostile}]}
        r = await c.post(
            f"/api/v1/orgs/{oid}/comfyui-imports",
            json={"data": json.dumps(payload), "encoding": "json"},
            headers=h,
        )
        assert r.status_code == 201, f"widgets={hostile!r}: {r.status_code} {r.text[:200]}"
        # Non-list widgets are discarded — never scanned for model refs
        assert r.json()["data"]["dependency_report"]["models"] == []


@pytest.mark.asyncio
async def test_non_dict_api_inputs_no_crash(c):
    """API-format `inputs` may be list/str/int — non-empty ones were kept by
    `or {}` (truthy) and .values() AttributeError'd (500)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for hostile in ([1, 2, 3], "evil", 99):
        payload = {"1": {"class_type": "KSampler", "inputs": hostile}}
        r = await c.post(
            f"/api/v1/orgs/{oid}/comfyui-imports",
            json={"data": json.dumps(payload), "encoding": "json"},
            headers=h,
        )
        assert r.status_code == 201, f"inputs={hostile!r}: {r.status_code} {r.text[:200]}"
        assert r.json()["data"]["format_detected"] == "api"


@pytest.mark.asyncio
async def test_node_count_capped_before_normalization(c):
    """The MAX_NODES cap must fire BEFORE per-node normalization — a dense
    payload packs ~300k minimal nodes into the size cap and normalizing
    them first burns seconds of CPU + ~80MB just to reject afterwards."""
    import time

    h, _ = await _auth(c)
    oid = await _org(c, h)
    payload = {"nodes": [{"type": "a"} for _ in range(100_000)], "links": []}
    t0 = time.time()
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(payload), "encoding": "json"},
        headers=h,
    )
    elapsed = time.time() - t0
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "IMPORT_TOO_COMPLEX"
    # Generous bound: JSON transport dominates; normalization would add seconds
    assert elapsed < 10, f"reject took {elapsed:.1f}s — cap likely after normalization"


@pytest.mark.asyncio
async def test_dependency_report_size_bounded(c):
    """2000 nodes with unique 100+-char class_types must not produce an
    unbounded JSONB report — listed types cap at 500, true total kept."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    payload = {"nodes": [{"type": f"Custom{i}" + "x" * 100} for i in range(1000)]}
    r = await c.post(
        f"/api/v1/orgs/{oid}/comfyui-imports",
        json={"data": json.dumps(payload), "encoding": "json"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    report = r.json()["data"]["dependency_report"]
    assert len(report["custom_nodes"]) == 500
    assert report["custom_node_types_total"] == 1000
    assert report["custom_node_count"] == 1000  # true node total preserved


def test_sanitize_hostile_megastring_fast():
    """NFKC on a multi-MB hostile string cost ~4.5s of CPU before the
    pre-slice fix (U+FDFA expands 18x) — a cheap DoS via any sanitized field."""
    import time

    from app.core.sanitize import sanitize_untrusted_text

    s = "ﷺ" * (1024 * 1024)
    t0 = time.time()
    out = sanitize_untrusted_text(s, 300)
    assert time.time() - t0 < 0.5
    assert len(out) == 300


def test_sanitize_preslice_keeps_legit_length():
    """Pre-slice headroom (8x) must not shorten legitimate invisible-heavy
    input below max_len."""
    from app.core.sanitize import sanitize_untrusted_text

    s = ("​" * 7 + "a") * 300  # 7 invisibles per visible char
    assert len(sanitize_untrusted_text(s, 300)) == 300


@pytest.mark.asyncio
async def test_hostile_png_chunk_walker(c):
    """PNG walker must survive truncated/oversized/looping chunk structures."""
    import struct
    import zlib

    h, _ = await _auth(c)
    oid = await _org(c, h)
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    hostiles = {
        "len_2^31": sig + struct.pack(">I", 2**31 - 1) + b"tEXt" + b"x" * 100,
        "len_2^32-1": sig + b"\xff\xff\xff\xff" + b"tEXt" + b"x" * 100,
        "no_iend": sig + chunk(b"IDAT", b"x" * 50) * 100,
        "text_no_null": sig + chunk(b"tEXt", b"workflowNOSEP") + chunk(b"IEND", b""),
        "truncated": sig + struct.pack(">I", 500) + b"tEXt" + b"short",
        "itxt_compressed": sig
        + chunk(b"iTXt", b"workflow\x00\x01\x00\x00\x00" + zlib.compress(b"{}"))
        + chunk(b"IEND", b""),
    }
    for name, raw in hostiles.items():
        r = await c.post(
            f"/api/v1/orgs/{oid}/comfyui-imports",
            json={"data": base64.b64encode(raw).decode(), "encoding": "base64"},
            headers=h,
        )
        # Clean 422 (no workflow found / bad json) — never a 500
        assert r.status_code == 422, f"{name}: {r.status_code} {r.text[:200]}"
