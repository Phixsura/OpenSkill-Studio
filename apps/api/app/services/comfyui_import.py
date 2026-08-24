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
                            found[keyword] = rest[trans_end + 1 :].decode(
                                "utf-8", errors="replace"
                            )
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
            api_nodes = [
                v for v in parsed.values() if isinstance(v, dict) and "class_type" in v
            ]
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
                    links_count += sum(
                        1 for val in inputs.values() if isinstance(val, list)
                    )
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
            ct = sanitize_untrusted_text(str(node.get("class_type") or ""), 120)
            class_counts[ct] = class_counts.get(ct, 0) + 1
            if ct not in COMFYUI_CORE_NODES:
                custom_counts[ct] = custom_counts.get(ct, 0) + 1
            if ct in INPUT_NODE_TYPES:
                input_nodes.append(ct)
            if ct in OUTPUT_NODE_TYPES:
                output_nodes.append(ct)
            if ct in NODE_CAPABILITY_MAP:
                capabilities.add(NODE_CAPABILITY_MAP[ct])
            confidence = "whitelist" if ct in MODEL_LOADER_NODES else "structural"
            for val in node.get("widgets_values") or []:
                if isinstance(val, str) and val.lower().endswith(MODEL_EXTENSIONS):
                    models.append(
                        {
                            "filename": sanitize_untrusted_text(val, 300),
                            "node_type": ct,
                            "confidence": confidence,
                        }
                    )

        core_count = sum(
            count for ct, count in class_counts.items() if ct in COMFYUI_CORE_NODES
        )
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
