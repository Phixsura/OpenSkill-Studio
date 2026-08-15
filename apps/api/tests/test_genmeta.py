"""Unit tests for generation-metadata extraction (app/core/genmeta.py).

Builds synthetic PNGs in-test so we exercise the real chunk parser against
both well-formed and hostile inputs.
"""

import json
import struct
import zlib

from app.core.genmeta import (
    extract_generation_metadata,
    extract_png_text_chunks,
    parse_a1111_infotext,
    parse_comfyui_prompt,
)

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + ctype
        + data
        + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    )


def _png(*chunks: bytes) -> bytes:
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
    iend = _chunk(b"IEND", b"")
    return PNG_SIG + ihdr + b"".join(chunks) + iend


def _text_chunk(keyword: str, text: str) -> bytes:
    return _chunk(b"tEXt", keyword.encode("latin-1") + b"\x00" + text.encode("latin-1"))


def _ztxt_chunk(keyword: str, text: str) -> bytes:
    return _chunk(
        b"zTXt", keyword.encode("latin-1") + b"\x00\x00" + zlib.compress(text.encode("utf-8"))
    )


A1111 = (
    "masterpiece, best quality, 1girl, knight armor\n"
    "Negative prompt: lowres, bad anatomy, watermark\n"
    "Steps: 30, Sampler: Euler a, CFG scale: 4, Seed: 2049363429, "
    "Size: 832x1216, Model hash: 748cm123ab, Model: WAI-illustrious, Clip skip: 2"
)


# ── chunk walker ──


def test_text_chunk_extracted():
    png = _png(_text_chunk("parameters", A1111))
    chunks = extract_png_text_chunks(png)
    assert chunks["parameters"] == A1111


def test_ztxt_chunk_inflated():
    png = _png(_ztxt_chunk("parameters", A1111))
    chunks = extract_png_text_chunks(png)
    assert "Steps: 30" in chunks["parameters"]


def test_not_a_png():
    assert extract_png_text_chunks(b"\xff\xd8\xffJPEG data here") == {}


def test_truncated_png():
    png = _png(_text_chunk("parameters", A1111))
    assert isinstance(extract_png_text_chunks(png[:30]), dict)  # no crash


def test_corrupt_length_field():
    # Chunk claims huge length beyond file end
    bad = PNG_SIG + struct.pack(">I", 2**31) + b"tEXtx"
    assert extract_png_text_chunks(bad) == {}


def test_zip_bomb_rejected():
    # 100MB of zeros compresses tiny; inflation cap must refuse it
    bomb = zlib.compress(b"\x00" * (100 * 1024 * 1024))
    png = _png(_chunk(b"zTXt", b"parameters\x00\x00" + bomb))
    chunks = extract_png_text_chunks(png)
    assert "parameters" not in chunks


def test_duplicate_keyword_first_wins():
    png = _png(_text_chunk("parameters", "first"), _text_chunk("parameters", "second"))
    assert extract_png_text_chunks(png)["parameters"] == "first"


def test_max_chunks_cap():
    many = b"".join(_text_chunk(f"k{i}", "v") for i in range(100))
    chunks = extract_png_text_chunks(PNG_SIG + many)
    assert len(chunks) <= 64


# ── A1111 parser ──


def test_a1111_full_parse():
    r = parse_a1111_infotext(A1111)
    assert r["source"] == "a1111"
    assert r["prompt"].startswith("masterpiece")
    assert r["negative_prompt"].startswith("lowres")
    assert r["steps"] == 30
    assert r["sampler"] == "Euler a"
    assert r["cfg_scale"] == 4.0
    assert r["seed"] == 2049363429
    assert r["size"] == "832x1216"
    assert r["model"] == "WAI-illustrious"
    assert r["model_hash"] == "748cm123ab"
    assert r["clip_skip"] == 2


def test_a1111_no_negative():
    r = parse_a1111_infotext("a castle\nSteps: 20, Seed: 42")
    assert r["prompt"] == "a castle"
    assert "negative_prompt" not in r
    assert r["seed"] == 42


def test_a1111_multiline_prompt():
    text = "line one\nline two\nNegative prompt: bad\nSteps: 10"
    r = parse_a1111_infotext(text)
    assert r["prompt"] == "line one\nline two"


def test_a1111_garbage_returns_none():
    assert parse_a1111_infotext("") is None
    assert parse_a1111_infotext("just some words") is None  # no params, no structure


def test_a1111_prompt_truncated_at_10k():
    r = parse_a1111_infotext("x" * 50000 + "\nSteps: 5")
    assert len(r["prompt"]) == 10000


# ── ComfyUI parser ──


def _comfy_graph():
    return json.dumps(
        {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 123456789,
                    "steps": 25,
                    "cfg": 7.5,
                    "sampler_name": "dpmpp_2m",
                    "model": ["4", 0],
                },
            },
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "a scenic mountain"}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality"}},
        }
    )


def test_comfyui_parse():
    r = parse_comfyui_prompt(_comfy_graph())
    assert r["source"] == "comfyui"
    assert r["seed"] == 123456789
    assert r["steps"] == 25
    assert r["cfg_scale"] == 7.5
    assert r["sampler"] == "dpmpp_2m"
    assert r["prompt"] == "a scenic mountain"
    assert r["negative_prompt"] == "blurry, low quality"


def test_comfyui_not_json():
    assert parse_comfyui_prompt("{invalid json") is None


def test_comfyui_json_but_not_graph():
    assert parse_comfyui_prompt('["a", "list"]') is None
    assert parse_comfyui_prompt('{"empty": {}}') is None


def test_comfyui_oversized_rejected():
    big = json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 1, "pad": "x" * 300000}}})
    assert parse_comfyui_prompt(big) is None


# ── end-to-end entry point ──


def test_extract_from_a1111_png():
    png = _png(_text_chunk("parameters", A1111))
    r = extract_generation_metadata(png, "image/png")
    assert r["source"] == "a1111"
    assert r["seed"] == 2049363429


def test_extract_from_comfyui_png():
    png = _png(
        _text_chunk("prompt", _comfy_graph()),
        _text_chunk("workflow", '{"nodes": []}'),
    )
    r = extract_generation_metadata(png, "image/png")
    assert r["source"] == "comfyui"
    assert r["seed"] == 123456789
    assert r["has_comfyui_workflow"] is True
    assert r["workflow_bytes"] > 0


def test_extract_plain_png_returns_none():
    assert extract_generation_metadata(_png(), "image/png") is None


def test_extract_non_png_returns_none():
    assert extract_generation_metadata(b"\xff\xd8\xff jpeg", "image/jpeg") is None
    # PNG mime but JPEG content — chunk walker rejects
    assert extract_generation_metadata(b"\xff\xd8\xff jpeg", "image/png") is None


def test_extract_a1111_preferred_over_comfy():
    png = _png(
        _text_chunk("parameters", A1111),
        _text_chunk("prompt", _comfy_graph()),
    )
    r = extract_generation_metadata(png, "image/png")
    assert r["source"] == "a1111"


def test_extract_hostile_deep_json_safe():
    deep = '{"1":' * 200 + "{}" + "}" * 200
    png = _png(_text_chunk("prompt", deep))
    # Must not raise; result is None or a dict without crash
    r = extract_generation_metadata(png, "image/png")
    assert r is None or isinstance(r, dict)
