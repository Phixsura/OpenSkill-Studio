"""Safe ComfyUI workflow import (ADR-010 D4 layer 4).

Parse-only pipeline: size caps → format detection (lenient) → structural
caps → dependency extraction → provenance storage.

NEVER executes imported workflows, fetches URLs, resolves models, or
installs anything. This module performs no network I/O of any kind.
"""

import hashlib
import json
import re

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.sanitize import sanitize_untrusted_text
from app.exceptions import AppError
from app.models.workflow_pack import ComfyUIImport, WorkflowPack

log = structlog.get_logger()

MAX_IMPORT_BYTES = 5 * 1024 * 1024  # 5MB pre-parse cap
MAX_NODES = 2000
MAX_LINKS = 10000

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Core ComfyUI node class_types — vendored snapshot 2026-08.
# Anything NOT in this set is reported as a custom-node dependency.
COMFYUI_CORE_NODES = frozenset(
    {
        "KSampler",
        "KSamplerAdvanced",
        "CheckpointLoaderSimple",
        "CLIPTextEncode",
        "CLIPSetLastLayer",
        "VAEDecode",
        "VAEEncode",
        "VAEEncodeForInpaint",
        "VAELoader",
        "EmptyLatentImage",
        "LatentUpscale",
        "LatentUpscaleBy",
        "LoadImage",
        "LoadImageMask",
        "SaveImage",
        "PreviewImage",
        "ImageScale",
        "ImageScaleBy",
        "ImageInvert",
        "ImagePadForOutpaint",
        "ConditioningCombine",
        "ConditioningAverage",
        "ConditioningConcat",
        "ConditioningSetArea",
        "ConditioningSetAreaPercentage",
        "ConditioningSetMask",
        "ConditioningZeroOut",
        "ControlNetLoader",
        "DiffControlNetLoader",
        "ControlNetApply",
        "ControlNetApplyAdvanced",
        "LoraLoader",
        "LoraLoaderModelOnly",
        "CLIPLoader",
        "DualCLIPLoader",
        "UNETLoader",
        "StyleModelLoader",
        "StyleModelApply",
        "CLIPVisionLoader",
        "CLIPVisionEncode",
        "unCLIPConditioning",
        "unCLIPCheckpointLoader",
        "GLIGENLoader",
        "GLIGENTextBoxApply",
        "InpaintModelConditioning",
        "FreeU",
        "FreeU_V2",
        "HyperTile",
        "PerpNeg",
        "PatchModelAddDownscale",
        "TomePatchModel",
        "RepeatLatentBatch",
        "LatentComposite",
        "LatentBlend",
        "LatentRotate",
        "LatentFlip",
        "LatentCrop",
        "SetLatentNoiseMask",
        "LatentFromBatch",
        "ImageBatch",
        "ImageCrop",
        "ImageBlend",
        "ImageBlur",
        "ImageQuantize",
        "ImageSharpen",
        "ImageCompositeMasked",
        "EmptyImage",
        "MaskToImage",
        "ImageToMask",
        "SolidMask",
        "InvertMask",
        "CropMask",
        "MaskComposite",
        "FeatherMask",
        "GrowMask",
        "PorterDuffImageComposite",
        "SplitImageWithAlpha",
        "JoinImageWithAlpha",
    }
)

# Core node → platform capability mapping (for draft pack generation)
NODE_CAPABILITY_MAP: dict[str, str] = {
    "KSampler": "image_generation",
    "KSamplerAdvanced": "image_generation",
    "ControlNetApply": "image_editing",
    "ControlNetApplyAdvanced": "image_editing",
    "InpaintModelConditioning": "image_editing",
    "VAEEncodeForInpaint": "image_editing",
    "ImageBlend": "image_editing",
    "ImageBlur": "image_editing",
    "ImageSharpen": "image_editing",
    "ImageCompositeMasked": "image_editing",
    "LatentUpscale": "upscale",
    "LatentUpscaleBy": "upscale",
    "ImageScale": "upscale",
    "ImageScaleBy": "upscale",
}

MODEL_EXTENSIONS = (".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf", ".sft")
INPUT_NODE_TYPES = {"LoadImage", "LoadImageMask"}
OUTPUT_NODE_TYPES = {"SaveImage", "PreviewImage", "VHS_VideoCombine"}
# Loaders whose widget values are known model references (high confidence)
MODEL_LOADER_NODES = {
    "CheckpointLoaderSimple",
    "LoraLoader",
    "LoraLoaderModelOnly",
    "VAELoader",
    "ControlNetLoader",
    "DiffControlNetLoader",
    "UNETLoader",
    "CLIPLoader",
    "DualCLIPLoader",
    "unCLIPCheckpointLoader",
}


def _parsed_has_nul(v) -> bool:
    """True if any string (key or value) anywhere in the parsed structure
    contains a NUL byte.

    json.loads turns the 6-char escape ``\\u0000`` into a real NUL inside the
    parsed dict, so scanning json_text for a literal NUL misses it — the NUL
    then reaches the original_json JSONB insert and crashes asyncpg with
    UntranslatableCharacterError (a 500). Restricted to NUL: unlike run
    inputs, imports intentionally tolerate other control chars and strip them
    during report sanitization (sanitize_untrusted_text), and NUL is the only
    character JSONB cannot store.

    ITERATIVE, not recursive — json.loads succeeds at nesting depths far past
    Python's recursion limit, so a recursive scan on a ~1000-deep hostile
    import would RecursionError into the very 500 this guard closes.
    """
    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            if "\x00" in cur:
                return True
        elif isinstance(cur, dict):
            stack.extend(cur.keys())
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return False


def _extract_png_workflow(raw: bytes) -> str | None:
    """Extract 'workflow' or 'prompt' text chunk from PNG bytes.

    Pure-Python chunk walker — no PIL, no execution, no network.
    """
    pos = len(PNG_SIGNATURE)
    found: dict[str, str] = {}
    while pos + 8 <= len(raw):
        length = int.from_bytes(raw[pos : pos + 4], "big")
        ctype = raw[pos + 4 : pos + 8]
        data_start = pos + 8
        data_end = data_start + length
        if data_end + 4 > len(raw):
            break
        data = raw[data_start:data_end]
        if ctype == b"tEXt":
            null_idx = data.find(b"\x00")
            if null_idx > 0:
                keyword = data[:null_idx].decode("latin-1", errors="replace")
                if keyword in ("workflow", "prompt"):
                    found[keyword] = data[null_idx + 1 :].decode("latin-1", errors="replace")
        elif ctype == b"iTXt":
            null_idx = data.find(b"\x00")
            if null_idx > 0:
                keyword = data[:null_idx].decode("latin-1", errors="replace")
                if keyword in ("workflow", "prompt") and len(data) > null_idx + 3:
                    compression_flag = data[null_idx + 1]
                    rest = data[null_idx + 3 :]
                    # language\0translated\0text
                    lang_end = rest.find(b"\x00")
                    if lang_end >= 0:
                        trans_end = rest.find(b"\x00", lang_end + 1)
                        if trans_end >= 0 and compression_flag == 0:
                            found[keyword] = rest[trans_end + 1 :].decode("utf-8", errors="replace")
        elif ctype == b"IEND":
            break
        pos = data_end + 4  # skip CRC
    # Prefer full UI workflow over API prompt
    return found.get("workflow") or found.get("prompt")


class ComfyUIImportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_and_import(self, org_id: str, raw: bytes, created_by: str) -> ComfyUIImport:
        if len(raw) > MAX_IMPORT_BYTES:
            raise AppError(
                "IMPORT_TOO_LARGE",
                f"Import is {len(raw)} bytes; max {MAX_IMPORT_BYTES}",
                422,
            )

        format_detected = None
        json_text: str
        if raw.startswith(PNG_SIGNATURE):
            extracted = _extract_png_workflow(raw)
            if extracted is None:
                raise AppError(
                    "NO_WORKFLOW_IN_PNG", "PNG contains no embedded workflow metadata", 422
                )
            json_text = extracted
            format_detected = "png_embedded"
        else:
            json_text = raw.decode("utf-8", errors="replace")

        try:
            parsed = json.loads(json_text)
        except (ValueError, TypeError, RecursionError):
            # RecursionError: deeply nested JSON (e.g. 50k '[' chars) blows the
            # parser's recursion guard — must be a 422, not an unhandled 500
            raise AppError("INVALID_JSON", "Import is not valid JSON", 422) from None

        if not isinstance(parsed, dict):
            raise AppError("UNRECOGNIZED_FORMAT", "Import is not a recognized ComfyUI format", 422)

        # A NUL embedded in a JSON string value (valid JSON) would be stored
        # verbatim into the original_json JSONB column and crash asyncpg with
        # UntranslatableCharacterError (a 500). Reject as a clean 422.
        # Cheap fast path first (literal NUL in the raw text), then the real
        # guard: a recursive scan of the PARSED structure, because json.loads
        # converts \\u0000 escapes into real NULs the text scan cannot see.
        # Applies to the PNG-embedded path too — json_text/parsed come from
        # the extracted chunk there.
        if "\x00" in json_text or _parsed_has_nul(parsed):
            raise AppError(
                "INVALID_CONTENT",
                "Import contains NUL characters that are not allowed",
                422,
            )

        # Non-finite floats: json.loads accepts the bare tokens NaN/Infinity/
        # -Infinity and yields real float('nan')/float('inf'), which pass the
        # NUL/depth/size checks (those inspect str, not float) but crash the
        # asyncpg JSONB write of original_json with 22P02 (a 500). Every other
        # JSONB write surface screens for this (R73); the import path did not.
        from app.schemas.base import reject_nonfinite_json

        try:
            reject_nonfinite_json(parsed, "Import")
        except ValueError as exc:
            raise AppError(
                "INVALID_CONTENT",
                "Import contains NaN or Infinity values that are not allowed",
                422,
            ) from exc

        # Depth cap: original_json is stored VERBATIM and echoed by the
        # detail read (?include_original=true) — json.loads accepts ~900
        # levels while pydantic's serializer dies around 400, so a deep
        # block smuggled next to a valid nodes[] array would make the
        # import row permanently unreadable (R51/R53 class). Real ComfyUI
        # exports nest a handful of levels.
        from app.schemas.base import max_json_depth

        if max_json_depth(parsed) > 64:
            raise AppError(
                "IMPORT_TOO_DEEP",
                "Import JSON is nested deeper than 64 levels",
                422,
            )

        # Lenient format detection (ingestion tolerance — C2)
        nodes: list[dict] = []
        links_count = 0
        too_complex = AppError(
            "IMPORT_TOO_COMPLEX",
            f"Import exceeds structural caps ({MAX_NODES} nodes / {MAX_LINKS} links)",
            422,
        )
        if isinstance(parsed.get("nodes"), list) and all(
            isinstance(n, dict) and "type" in n for n in parsed["nodes"]
        ):
            # UI format
            if format_detected is None:
                format_detected = "ui"
            # Cap BEFORE normalization: a 5MB payload can pack ~300k minimal
            # nodes — normalizing them first costs seconds of CPU + ~80MB
            # per request just to reject it afterwards
            if len(parsed["nodes"]) > MAX_NODES:
                raise too_complex
            nodes = [
                {
                    "class_type": str(n.get("type", "")),
                    "title": str(n.get("title", "")) if n.get("title") else None,
                    # widgets_values may be any JSON type in hostile input —
                    # a scalar (5, true) is truthy, so `or []` keeps it and
                    # the report loop's iteration would TypeError (500)
                    "widgets_values": n["widgets_values"]
                    if isinstance(n.get("widgets_values"), list)
                    else [],
                }
                for n in parsed["nodes"]
            ]
            links = parsed.get("links")
            links_count = len(links) if isinstance(links, list) else 0
        else:
            api_nodes = [v for v in parsed.values() if isinstance(v, dict) and "class_type" in v]
            if api_nodes:
                if format_detected is None:
                    format_detected = "api"
                if len(api_nodes) > MAX_NODES:
                    raise too_complex
                for v in api_nodes:
                    # inputs may be any JSON type — a non-empty list/str is
                    # truthy, so `or {}` keeps it and .values() AttributeErrors
                    inputs = v.get("inputs")
                    if not isinstance(inputs, dict):
                        inputs = {}
                    widget_like = [
                        val for val in inputs.values() if isinstance(val, str | int | float)
                    ]
                    nodes.append(
                        {
                            "class_type": str(v.get("class_type", "")),
                            "title": str(v.get("_meta", {}).get("title", ""))
                            if isinstance(v.get("_meta"), dict)
                            else None,
                            "widgets_values": widget_like,
                        }
                    )
                    links_count += sum(1 for val in inputs.values() if isinstance(val, list))
            else:
                raise AppError(
                    "UNRECOGNIZED_FORMAT", "Import is not a recognized ComfyUI format", 422
                )

        if len(nodes) > MAX_NODES or links_count > MAX_LINKS:
            raise too_complex

        report = self._build_dependency_report(nodes)

        imp = ComfyUIImport(
            org_id=org_id,
            original_json=parsed,
            original_sha256=hashlib.sha256(raw).hexdigest(),
            format_detected=format_detected,
            dependency_report=report,
            created_by=created_by,
        )
        self.db.add(imp)
        await self.db.flush()
        log.info(
            "comfyui_imported",
            import_id=imp.id,
            org_id=org_id,
            fmt=format_detected,
            nodes=len(nodes),
            custom=report["custom_node_count"],
        )
        return imp

    @staticmethod
    def _build_dependency_report(nodes: list[dict]) -> dict:
        class_counts: dict[str, int] = {}
        custom_counts: dict[str, int] = {}
        models: list[dict] = []
        input_nodes: list[str] = []
        output_nodes: list[str] = []
        capabilities: set[str] = set()

        for node in nodes:
            # Classify on the RAW class_type; sanitize ONLY for the stored/
            # displayed label (R86). sanitize_untrusted_text runs NFKC, which
            # folds a crafted fullwidth "ＫSampler" to the core name "KSampler"
            # — so classifying on the sanitized form counts a disguised custom
            # node as a trusted core node and ERASES it from the custom-node
            # dependency warning (the report lies about what the workflow needs).
            # Real ComfyUI class_types are plain ASCII identifiers, so NFKC is a
            # no-op on legitimate input and this changes nothing for them.
            raw_ct = str(node.get("class_type") or "")
            ct = sanitize_untrusted_text(raw_ct, 120)
            class_counts[ct] = class_counts.get(ct, 0) + 1
            if raw_ct not in COMFYUI_CORE_NODES:
                custom_counts[ct] = custom_counts.get(ct, 0) + 1
            if raw_ct in INPUT_NODE_TYPES:
                input_nodes.append(ct)
            if raw_ct in OUTPUT_NODE_TYPES:
                output_nodes.append(ct)
            if raw_ct in NODE_CAPABILITY_MAP:
                capabilities.add(NODE_CAPABILITY_MAP[raw_ct])
            confidence = "whitelist" if raw_ct in MODEL_LOADER_NODES else "structural"
            for val in node.get("widgets_values") or []:
                if isinstance(val, str) and val.lower().endswith(MODEL_EXTENSIONS):
                    models.append(
                        {
                            "filename": sanitize_untrusted_text(val, 300),
                            "node_type": ct,
                            "confidence": confidence,
                        }
                    )

        # Every node is core or custom; derive core from the raw-based custom
        # tally so a fold-disguised node can never inflate the core count.
        core_count = len(nodes) - sum(custom_counts.values())
        return {
            # Cap listed types (true totals preserved in custom_node_count):
            # 2000 nodes x 120-char class_types is a ~300KB JSONB row otherwise
            "custom_nodes": [
                {"class_type": ct, "count": count}
                for ct, count in sorted(custom_counts.items())[:500]
            ],
            "custom_node_types_total": len(custom_counts),
            "models": models[:100],
            "input_nodes": input_nodes,
            "output_nodes": output_nodes,
            "core_node_count": core_count,
            "custom_node_count": sum(custom_counts.values()),
            "total_nodes": len(nodes),
            "capabilities_detected": sorted(capabilities),
        }

    async def list_imports(self, org_id: str) -> list[ComfyUIImport]:
        result = await self.db.execute(
            select(ComfyUIImport)
            .where(ComfyUIImport.org_id == org_id)
            .order_by(ComfyUIImport.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_import(self, import_id: str, org_id: str) -> ComfyUIImport:
        imp = await self.db.get(ComfyUIImport, import_id)
        if imp is None or imp.org_id != org_id:
            raise AppError("IMPORT_NOT_FOUND", "ComfyUI import not found", 404)
        return imp

    async def create_pack_draft(
        self, import_id: str, org_id: str, created_by: str, name: str
    ) -> WorkflowPack:
        """Create a draft Workflow Pack from an import's detected capabilities.

        Always lands as a DRAFT requiring human editing/confirmation — the
        imported graph is never executed or auto-published.
        """
        from app.services.workflow_pack import WorkflowPackService

        imp = await self.get_import(import_id, org_id)
        report = imp.dependency_report or {}

        steps: list[dict] = []
        for capability in report.get("capabilities_detected", []):
            steps.append(
                {
                    "id": f"comfy_{capability}"[:64],
                    "type": "provider_action",
                    "name": capability.replace("_", " ").title(),
                    "config": {"capability": capability},
                    "inputs": [],
                    "outputs": [{"port": "result", "type": "image"}],
                }
            )
        custom = report.get("custom_nodes", [])
        if custom:
            # Restrict listed class_types to a safe charset: a crafted
            # class_type like '{{inputs.x}}' or 'data:...;base64,' would
            # otherwise land verbatim in the instruction config and make the
            # generated definition permanently fail validate_or_raise
            # (WF_EXPR_INVALID / WF_DATA_URI_REJECTED).
            listing = ", ".join(
                re.sub(r"[^A-Za-z0-9_.: -]", "", sanitize_untrusted_text(c["class_type"], 100))
                for c in custom[:50]
            )
            content = (
                "This workflow was imported from ComfyUI and uses custom nodes that "
                f"need manual mapping: {listing}"
            )[:4000]
            steps.append(
                {
                    "id": "comfy_unmapped",
                    "type": "instruction",
                    "name": "Unmapped custom nodes",
                    "config": {"content": content},
                    "inputs": [],
                    "outputs": [],
                }
            )
        if not steps:
            steps.append(
                {
                    "id": "comfy_imported",
                    "type": "instruction",
                    "name": "Imported workflow",
                    "config": {
                        "content": "Imported ComfyUI workflow — add steps to map its behavior."
                    },
                    "inputs": [],
                    "outputs": [],
                }
            )

        definition = {
            "schema_version": 1,
            "inputs": [
                {"key": "source_image", "type": "image", "label": "Source image", "required": False}
            ],
            "outputs": [],
            "steps": steps,
            "edges": [],
            "ui": {},
        }

        pack_svc = WorkflowPackService(self.db)
        pack = await pack_svc.create_pack(
            org_id,
            created_by,
            name=name,
            summary="Imported from ComfyUI",
            provenance={
                "source": "comfyui_import",
                "import_id": imp.id,
                "original_sha256": imp.original_sha256,
            },
        )
        await pack_svc.update_definition(pack.id, org_id, definition)

        imp.pack_id = pack.id
        imp.status = "mapped"
        await self.db.flush()
        return pack
