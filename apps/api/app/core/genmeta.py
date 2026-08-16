"""Generation-metadata extraction from AI-generated images.

AI creation tools embed their generation parameters inside the files they
produce: Automatic1111-style tools write an "infotext" string into the PNG
`parameters` tEXt chunk; ComfyUI writes its execution graph JSON into a
`prompt` chunk and the full UI graph into a `workflow` chunk.

Everything here treats file content as UNTRUSTED input (per ComfyUI's own
documentation): hard size caps, no recursion into attacker-controlled
structures beyond bounded scans, and any malformed data yields None/{} —
never an exception.

Pure stdlib — no new dependencies.
"""

import json
import math
import re
import struct
import zlib

import structlog

log = structlog.get_logger()

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Hard caps (untrusted input)
MAX_CHUNKS_SCANNED = 64
MAX_CHUNK_BYTES = 512 * 1024  # raw chunk size we are willing to read
MAX_INFLATED_BYTES = 1024 * 1024  # zTXt/iTXt decompression cap (zip-bomb guard)
MAX_TOTAL_TEXT = 2 * 1024 * 1024  # total extracted text across all chunks
MAX_COMFY_JSON = 256 * 1024  # ComfyUI prompt JSON we are willing to parse


def extract_png_text_chunks(data: bytes) -> dict[str, str]:
    """Walk PNG chunks and return {keyword: text} from tEXt/zTXt/iTXt.

    Returns {} for anything that is not a well-formed PNG. Never raises.
    """
    out: dict[str, str] = {}
    if not data.startswith(PNG_SIGNATURE):
        return out

    pos = len(PNG_SIGNATURE)
    total_text = 0
    chunks_seen = 0

    try:
        while pos + 8 <= len(data) and chunks_seen < MAX_CHUNKS_SCANNED:
            length, ctype = struct.unpack(">I4s", data[pos : pos + 8])
            pos += 8
            chunks_seen += 1

            if length > len(data) - pos:
                break  # truncated file
            chunk = data[pos : pos + length] if length <= MAX_CHUNK_BYTES else b""
            pos += length + 4  # skip data + CRC

            if ctype == b"IEND":
                break
            if not chunk:
                continue

            text: str | None = None
            keyword: str | None = None

            if ctype == b"tEXt":
                # keyword\0text, both latin-1
                sep = chunk.find(b"\x00")
                if 0 < sep < 80:
                    keyword = chunk[:sep].decode("latin-1", errors="replace")
                    text = chunk[sep + 1 :].decode("latin-1", errors="replace")

            elif ctype == b"zTXt":
                # keyword\0compression_method(1 byte)\0-deflate stream
                sep = chunk.find(b"\x00")
                if 0 < sep < 80 and len(chunk) > sep + 2 and chunk[sep + 1] == 0:
                    keyword = chunk[:sep].decode("latin-1", errors="replace")
                    text = _safe_inflate(chunk[sep + 2 :])

            elif ctype == b"iTXt":
                # keyword\0compressed_flag\0compression_method\0lang\0translated\0text
                sep = chunk.find(b"\x00")
                if 0 < sep < 80 and len(chunk) > sep + 3:
                    keyword = chunk[:sep].decode("latin-1", errors="replace")
                    compressed = chunk[sep + 1]
                    rest = chunk[sep + 3 :]
                    # skip language tag and translated keyword (two \0-terminated)
                    lang_end = rest.find(b"\x00")
                    if lang_end >= 0:
                        trans_end = rest.find(b"\x00", lang_end + 1)
                        if trans_end >= 0:
                            payload = rest[trans_end + 1 :]
                            if compressed == 0:
                                text = payload.decode("utf-8", errors="replace")
                            else:
                                text = _safe_inflate(payload)

            if keyword and text:
                total_text += len(text)
                if total_text > MAX_TOTAL_TEXT:
                    break
                # first occurrence wins (defensive against duplicate-key tricks)
                out.setdefault(keyword, text)
    except Exception:  # noqa: BLE001 — untrusted input, fail closed
        return out

    return out


def _safe_inflate(payload: bytes) -> str | None:
    """Inflate a deflate stream with a decompression-size cap."""
    try:
        d = zlib.decompressobj()
        raw = d.decompress(payload, MAX_INFLATED_BYTES)
        if d.unconsumed_tail:
            return None  # would exceed cap — likely a zip bomb
        return raw.decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return None


# ── A1111 infotext ────────────────────────────────────────────

_A1111_KV = re.compile(r"([A-Za-z][A-Za-z0-9 _]*):\s*([^,]*)")

# Keys we surface, mapped to normalized names + coercion
_A1111_KEYS = {
    "steps": ("steps", int),
    "sampler": ("sampler", str),
    "cfg scale": ("cfg_scale", float),
    "seed": ("seed", int),
    "size": ("size", str),
    "model": ("model", str),
    "model hash": ("model_hash", str),
    "clip skip": ("clip_skip", int),
}


def parse_a1111_infotext(text: str) -> dict | None:
    """Parse an Automatic1111 'parameters' infotext block.

    Format:
        <prompt lines...>
        Negative prompt: <negative lines...>
        Steps: 30, Sampler: Euler a, CFG scale: 4, Seed: 123, Size: 832x1216, ...
    """
    if not text or len(text) > MAX_TOTAL_TEXT:
        return None
    try:
        lines = text.strip().split("\n")
        # The settings line is the last line containing "Steps:"
        settings_idx = None
        for i in range(len(lines) - 1, -1, -1):
            if "Steps:" in lines[i]:
                settings_idx = i
                break

        neg_idx = None
        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                neg_idx = i
                break

        prompt_end = neg_idx if neg_idx is not None else settings_idx
        prompt = "\n".join(lines[:prompt_end]).strip() if prompt_end else text.strip()
        if prompt_end is None:
            prompt = text.strip()

        negative = None
        if neg_idx is not None:
            neg_end = settings_idx if settings_idx is not None else len(lines)
            neg_lines = lines[neg_idx:neg_end]
            neg_lines[0] = neg_lines[0][len("Negative prompt:") :]
            negative = "\n".join(neg_lines).strip() or None

        result: dict = {"source": "a1111"}
        if prompt:
            result["prompt"] = prompt[:10000]
        if negative:
            result["negative_prompt"] = negative[:10000]

        if settings_idx is not None:
            for m in _A1111_KV.finditer(lines[settings_idx]):
                key = m.group(1).strip().lower()
                val = m.group(2).strip()
                if key in _A1111_KEYS and val:
                    name, coerce = _A1111_KEYS[key]
                    try:
                        parsed = coerce(val) if coerce is not str else val[:200]
                    except (ValueError, TypeError):
                        continue
                    # Hostile numerics survive coercion but break the pipeline:
                    # float('inf')/nan serialize as Infinity/NaN (invalid JSON
                    # that crashes the frontend's JSON.parse), and unbounded
                    # ints overflow downstream consumers. Clamp to sane ranges.
                    if coerce is float and not math.isfinite(parsed):
                        continue
                    if coerce is int and not -(2**63) < parsed < 2**63:
                        continue
                    result[name] = parsed

        # A bare prompt with no settings line and no negative prompt is just
        # arbitrary text — not evidence of A1111 provenance.
        if settings_idx is None and neg_idx is None:
            return None
        if len(result) <= 1:
            return None
        return result
    except Exception:  # noqa: BLE001
        return None


# ── ComfyUI prompt graph ─────────────────────────────────────


def parse_comfyui_prompt(text: str) -> dict | None:
    """Best-effort extraction from a ComfyUI API-format prompt graph.

    The graph is {node_id: {class_type, inputs}}. We scan (bounded) for
    KSampler-style nodes (seed/steps/cfg/sampler_name) and CLIPTextEncode
    text fields for prompt/negative.
    """
    if not text or len(text) > MAX_COMFY_JSON:
        return None
    try:
        graph = json.loads(text)
        if not isinstance(graph, dict):
            return None

        result: dict = {"source": "comfyui"}
        texts: list[str] = []

        for _node_id, node in list(graph.items())[:200]:  # bounded scan
            if not isinstance(node, dict):
                continue
            ctype = node.get("class_type", "")
            inputs = node.get("inputs", {})
            if not isinstance(inputs, dict):
                continue

            if "KSampler" in str(ctype):
                for src, dst, coerce in (
                    ("seed", "seed", int),
                    ("steps", "steps", int),
                    ("cfg", "cfg_scale", float),
                    ("sampler_name", "sampler", str),
                ):
                    v = inputs.get(src)
                    if isinstance(v, (int, float, str)) and dst not in result:
                        try:
                            parsed = coerce(v) if coerce is not str else str(v)[:200]
                        except (ValueError, TypeError):
                            continue
                        # json.loads accepts Infinity/NaN literals, which
                        # re-serialize as invalid JSON — clamp like A1111.
                        if coerce is float and not math.isfinite(parsed):
                            continue
                        if coerce is int and not -(2**63) < parsed < 2**63:
                            continue
                        result[dst] = parsed

            elif "CLIPTextEncode" in str(ctype):
                t = inputs.get("text")
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip()[:10000])

        # Heuristic: first text = prompt, second = negative (standard txt2img graphs)
        if texts:
            result["prompt"] = texts[0]
            if len(texts) > 1:
                result["negative_prompt"] = texts[1]

        if len(result) <= 1:
            return None
        return result
    except Exception:  # noqa: BLE001
        return None


# ── Public entry point ───────────────────────────────────────


def extract_generation_metadata(data: bytes, mime_type: str) -> dict | None:
    """Extract generation parameters from an uploaded image, if present.

    Currently PNG only (the only format tools reliably embed metadata in).
    Returns a normalized dict or None. Never raises.
    """
    if mime_type.lower() != "image/png":
        return None

    chunks = extract_png_text_chunks(data)
    if not chunks:
        return None

    result: dict | None = None

    # Priority 1: A1111 infotext
    if "parameters" in chunks:
        result = parse_a1111_infotext(chunks["parameters"])

    # Priority 2: ComfyUI prompt graph
    if result is None and "prompt" in chunks:
        result = parse_comfyui_prompt(chunks["prompt"])

    # Flag workflow presence without storing the full graph
    if "workflow" in chunks:
        if result is None:
            result = {"source": "comfyui"}
        result["has_comfyui_workflow"] = True
        result["workflow_bytes"] = len(chunks["workflow"])

    if result:
        log.info("generation_metadata_extracted", source=result.get("source"))
    return result
