"""Workflow definition schema + full graph validator (ADR-010, D4).

Definitions are pure data over a CLOSED vocabulary of 7 step types and
8 I/O types. Validation accumulates ALL errors in one pass (Argo pattern),
each with a JSON pointer and machine code.

The no-code-execution guarantee lives here: no expressions beyond closed
moustache references, no data URIs, hard size caps, typed edges checked
against an explicit coercion matrix.
"""

import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from app.exceptions import AppError

# ── Closed vocabularies ───────────────────────────────────

STEP_TYPES = (
    "instruction",
    "prompt_template",
    "asset_input",
    "transform",
    "provider_action",
    "review_gate",
    "output",
)

IO_TYPES = ("text", "prompt", "image", "video", "audio", "reference_asset", "json", "selection")

# Automatic coercions: identity + prompt↔text ONLY. Everything else requires
# an explicit transform step (C1 resolution). Keep in sync with
# apps/web/src/components/workflow-editor/types.ts
COERCIBLE: dict[str, set[str]] = {
    "text": {"text", "prompt"},
    "prompt": {"prompt", "text"},
    "image": {"image"},
    "video": {"video"},
    "audio": {"audio"},
    "reference_asset": {"reference_asset"},
    "json": {"json"},
    "selection": {"selection"},
}

STEP_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
PORT_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
EXPR_RE = re.compile(r"\{\{\s*([a-z0-9_.]+)\s*\}\}")
# data: URIs and large base64 blobs are rejected — assets are ULID references
DATA_URI_RE = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,", re.IGNORECASE)
BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/=]{1024,}")

MAX_STEPS = 50
MAX_EDGES = 150
MAX_STEP_CONFIG_BYTES = 16 * 1024
MAX_DEFINITION_BYTES = 256 * 1024
MAX_INPUTS = 20
MAX_OUTPUTS = 20


# ── Port / edge / input / output shapes ───────────────────


class PortDef(BaseModel):
    port: str
    type: Literal[
        "text", "prompt", "image", "video", "audio", "reference_asset", "json", "selection"
    ]
    required: bool = True
    options: list[str] | None = None  # selection type only


class EdgeDef(BaseModel):
    id: str
    from_step: str
    from_port: str
    to_step: str
    to_port: str


class WorkflowInputDef(BaseModel):
    key: str
    type: Literal[
        "text", "prompt", "image", "video", "audio", "reference_asset", "json", "selection"
    ]
    label: str | None = None
    required: bool = True
    default: str | None = None
    options: list[str] | None = None


class WorkflowOutputDef(BaseModel):
    key: str
    type: Literal[
        "text", "prompt", "image", "video", "audio", "reference_asset", "json", "selection"
    ]
    from_step: str
    from_port: str


# ── Step configs (discriminated by step type) ─────────────


class InstructionConfig(BaseModel):
    content: str = Field(max_length=4000)


class PromptTemplateConfig(BaseModel):
    template: str = Field(max_length=4000)


class AssetInputConfig(BaseModel):
    accept_types: list[
        Literal["image", "video", "audio", "reference_asset"]
    ] = ["image"]


class TransformConfig(BaseModel):
    operation: Literal["crop", "resize", "concat_text", "select_field"]
    params: dict = {}


class ProviderActionConfig(BaseModel):
    capability: str = Field(max_length=64)
    required_features: list[str] = []
    binding_mode: Literal["auto", "preferred", "pinned"] = "auto"
    pinned_offering_id: str | None = None


class ReviewGateConfig(BaseModel):
    instructions: str | None = Field(default=None, max_length=2000)
    due_days: int = Field(default=7, ge=1, le=30)


class OutputConfig(BaseModel):
    pass


_CONFIG_SCHEMAS = {
    "instruction": InstructionConfig,
    "prompt_template": PromptTemplateConfig,
    "asset_input": AssetInputConfig,
    "transform": TransformConfig,
    "provider_action": ProviderActionConfig,
    "review_gate": ReviewGateConfig,
    "output": OutputConfig,
}


class StepDef(BaseModel):
    id: str
    type: Literal[
        "instruction",
        "prompt_template",
        "asset_input",
        "transform",
        "provider_action",
        "review_gate",
        "output",
    ]
    name: str = Field(max_length=200)
    config: dict = {}
    inputs: list[PortDef] = []
    outputs: list[PortDef] = []


class WorkflowDefinition(BaseModel):
    schema_version: int = 1
    inputs: list[WorkflowInputDef] = []
    outputs: list[WorkflowOutputDef] = []
    steps: list[StepDef] = []
    edges: list[EdgeDef] = []
    ui: dict = {}  # editor layout; excluded from release checksum


# ── Validator (accumulate ALL errors, Argo style) ─────────


def _err(code: str, pointer: str, message: str, meta: dict | None = None) -> dict:
    d = {"code": code, "pointer": pointer, "message": message}
    if meta:
        d["meta"] = meta
    return d


def validate_definition(raw: dict) -> tuple[WorkflowDefinition | None, list[dict]]:
    """Validate a workflow definition dict. Returns (parsed, errors).

    All structural errors are accumulated in one pass; parsed is None when
    the top-level shape itself cannot be parsed.
    """
    errors: list[dict] = []

    # Size cap first (cheap,防 DoS)
    import json as _json

    raw_bytes = len(_json.dumps(raw, ensure_ascii=False).encode())
    if raw_bytes > MAX_DEFINITION_BYTES:
        return None, [
            _err(
                "WF_TOO_LARGE",
                "",
                f"Definition is {raw_bytes} bytes; max {MAX_DEFINITION_BYTES}",
            )
        ]

    # data: URI / base64 blob rejection anywhere in the payload (D4)
    flat = _json.dumps(raw, ensure_ascii=False)
    if DATA_URI_RE.search(flat) or BASE64_BLOB_RE.search(flat):
        errors.append(
            _err(
                "WF_DATA_URI_REJECTED",
                "",
                "Definitions must reference assets by ID — inline data URIs / base64 blobs are not allowed",
            )
        )

    try:
        definition = WorkflowDefinition.model_validate(raw)
    except ValidationError as exc:
        for e in exc.errors():
            pointer = "/" + "/".join(str(p) for p in e["loc"])
            errors.append(_err("WF_SCHEMA_INVALID", pointer, e["msg"]))
        return None, errors

    steps = definition.steps
    edges = definition.edges

    # ── Counts ──
    if len(steps) > MAX_STEPS:
        errors.append(_err("WF_TOO_LARGE", "/steps", f"Max {MAX_STEPS} steps (got {len(steps)})"))
    if len(edges) > MAX_EDGES:
        errors.append(_err("WF_TOO_LARGE", "/edges", f"Max {MAX_EDGES} edges (got {len(edges)})"))
    if len(definition.inputs) > MAX_INPUTS:
        errors.append(_err("WF_TOO_LARGE", "/inputs", f"Max {MAX_INPUTS} workflow inputs"))
    if len(definition.outputs) > MAX_OUTPUTS:
        errors.append(_err("WF_TOO_LARGE", "/outputs", f"Max {MAX_OUTPUTS} workflow outputs"))

    # ── Step ids ──
    step_by_id: dict[str, StepDef] = {}
    for i, step in enumerate(steps):
        ptr = f"/steps/{i}"
        if not STEP_ID_RE.match(step.id):
            errors.append(
                _err(
                    "WF_INVALID_STEP_ID",
                    f"{ptr}/id",
                    f"Step id '{step.id}' must match ^[a-z][a-z0-9_]{{0,63}}$",
                )
            )
        if step.id in step_by_id:
            errors.append(_err("WF_DUPLICATE_STEP_ID", f"{ptr}/id", f"Duplicate step id '{step.id}'"))
        else:
            step_by_id[step.id] = step

        # Per-step config size
        cfg_bytes = len(_json.dumps(step.config, ensure_ascii=False).encode())
        if cfg_bytes > MAX_STEP_CONFIG_BYTES:
            errors.append(
                _err(
                    "WF_TOO_LARGE",
                    f"{ptr}/config",
                    f"Step config is {cfg_bytes} bytes; max {MAX_STEP_CONFIG_BYTES}",
                )
            )

        # Typed config validation per step type
        schema = _CONFIG_SCHEMAS[step.type]
        try:
            schema.model_validate(step.config)
        except ValidationError as exc:
            for e in exc.errors():
                sub = "/" + "/".join(str(p) for p in e["loc"])
                errors.append(_err("WF_CONFIG_INVALID", f"{ptr}/config{sub}", e["msg"]))

        # Port names
        seen_ports: set[str] = set()
        for j, port in enumerate(step.inputs + step.outputs):
            if not PORT_RE.match(port.port):
                errors.append(
                    _err("WF_INVALID_PORT", f"{ptr}/ports/{j}", f"Invalid port name '{port.port}'")
                )
            if port.port in seen_ports:
                errors.append(
                    _err("WF_DUPLICATE_PORT", f"{ptr}/ports/{j}", f"Duplicate port '{port.port}'")
                )
            seen_ports.add(port.port)

    # ── Workflow input keys ──
    input_keys: set[str] = set()
    for i, inp in enumerate(definition.inputs):
        if not PORT_RE.match(inp.key):
            errors.append(_err("WF_INVALID_PORT", f"/inputs/{i}/key", f"Invalid input key '{inp.key}'"))
        if inp.key in input_keys:
            errors.append(_err("WF_DUPLICATE_PORT", f"/inputs/{i}/key", f"Duplicate input '{inp.key}'"))
        input_keys.add(inp.key)
        # A selection input without options can never be satisfied at run
        # time (every value fails INVALID_INPUT_VALUE) — reject at publish
        if inp.type == "selection" and not inp.options:
            errors.append(
                _err(
                    "WF_SELECTION_NO_OPTIONS",
                    f"/inputs/{i}/options",
                    f"Selection input '{inp.key}' must declare at least one option",
                )
            )

    # ── Edges ──
    edge_ids: set[str] = set()
    incoming: dict[tuple[str, str], list[EdgeDef]] = {}
    adjacency: dict[str, set[str]] = {s.id: set() for s in steps}
    for i, edge in enumerate(edges):
        ptr = f"/edges/{i}"
        if edge.id in edge_ids:
            errors.append(_err("WF_DUPLICATE_EDGE_ID", f"{ptr}/id", f"Duplicate edge id '{edge.id}'"))
        edge_ids.add(edge.id)

        src = step_by_id.get(edge.from_step)
        dst = step_by_id.get(edge.to_step)
        if src is None:
            errors.append(
                _err("WF_EDGE_UNKNOWN_STEP", f"{ptr}/from_step", f"Unknown step '{edge.from_step}'")
            )
        if dst is None:
            errors.append(
                _err("WF_EDGE_UNKNOWN_STEP", f"{ptr}/to_step", f"Unknown step '{edge.to_step}'")
            )
        if src is None or dst is None:
            continue

        src_port = next((p for p in src.outputs if p.port == edge.from_port), None)
        dst_port = next((p for p in dst.inputs if p.port == edge.to_port), None)
        if src_port is None:
            errors.append(
                _err(
                    "WF_EDGE_UNKNOWN_PORT",
                    f"{ptr}/from_port",
                    f"Step '{edge.from_step}' has no output port '{edge.from_port}'",
                )
            )
        if dst_port is None:
            errors.append(
                _err(
                    "WF_EDGE_UNKNOWN_PORT",
                    f"{ptr}/to_port",
                    f"Step '{edge.to_step}' has no input port '{edge.to_port}'",
                )
            )
        if src_port and dst_port:
            # Coercion matrix check (identity + prompt↔text only)
            if dst_port.type not in COERCIBLE.get(src_port.type, set()):
                errors.append(
                    _err(
                        "WF_EDGE_TYPE_MISMATCH",
                        ptr,
                        f"Cannot connect {src_port.type} → {dst_port.type} "
                        f"({edge.from_step}.{edge.from_port} → {edge.to_step}.{edge.to_port}); "
                        "add an explicit transform step",
                        meta={"from_type": src_port.type, "to_type": dst_port.type},
                    )
                )
            incoming.setdefault((edge.to_step, edge.to_port), []).append(edge)
            adjacency[edge.from_step].add(edge.to_step)

    # ── Cycle detection (Kahn) ──
    if step_by_id:
        indegree = {sid: 0 for sid in step_by_id}
        for targets in adjacency.values():
            for t in targets:
                if t in indegree:
                    indegree[t] += 1
        queue = [sid for sid, d in indegree.items() if d == 0]
        visited = 0
        while queue:
            node = queue.pop()
            visited += 1
            for t in adjacency.get(node, set()):
                indegree[t] -= 1
                if indegree[t] == 0:
                    queue.append(t)
        if visited < len(step_by_id):
            cycle_steps = sorted(sid for sid, d in indegree.items() if d > 0)
            errors.append(
                _err(
                    "WF_GRAPH_CYCLE",
                    "/edges",
                    f"Workflow graph contains a cycle involving: {', '.join(cycle_steps)}",
                    meta={"cycle_steps": cycle_steps},
                )
            )

    # ── Required inputs satisfied ──
    # A required input port must have an incoming edge OR be fed by a workflow
    # input via moustache in the step config (checked below), OR belong to
    # asset_input steps (fed from run inputs at execution).
    for i, step in enumerate(steps):
        if step.type == "asset_input":
            continue
        for port in step.inputs:
            if port.required and (step.id, port.port) not in incoming:
                errors.append(
                    _err(
                        "WF_INPUT_UNSATISFIED",
                        f"/steps/{i}/inputs/{port.port}",
                        f"Required input '{step.id}.{port.port}' has no incoming edge",
                    )
                )

    # ── Moustache expression validation ──
    step_output_refs = {
        f"steps.{s.id}.outputs.{p.port}" for s in steps for p in s.outputs
    }
    input_refs = {f"inputs.{k}" for k in input_keys}
    for i, step in enumerate(steps):
        cfg_text = _json.dumps(step.config, ensure_ascii=False)
        for m in EXPR_RE.finditer(cfg_text):
            ref = m.group(1)
            if ref in input_refs or ref in step_output_refs:
                continue
            errors.append(
                _err(
                    "WF_EXPR_INVALID",
                    f"/steps/{i}/config",
                    f"Expression '{{{{{ref}}}}}' references an unknown input or step output",
                )
            )

    # ── Workflow outputs reference real ports ──
    for i, out in enumerate(definition.outputs):
        src = step_by_id.get(out.from_step)
        if src is None:
            errors.append(
                _err("WF_EDGE_UNKNOWN_STEP", f"/outputs/{i}/from_step", f"Unknown step '{out.from_step}'")
            )
            continue
        port = next((p for p in src.outputs if p.port == out.from_port), None)
        if port is None:
            errors.append(
                _err(
                    "WF_EDGE_UNKNOWN_PORT",
                    f"/outputs/{i}/from_port",
                    f"Step '{out.from_step}' has no output port '{out.from_port}'",
                )
            )
        elif out.type not in COERCIBLE.get(port.type, set()):
            errors.append(
                _err(
                    "WF_EDGE_TYPE_MISMATCH",
                    f"/outputs/{i}",
                    f"Workflow output '{out.key}' declares {out.type} but source port is {port.type}",
                )
            )

    # ── Unreachable steps (no path from any entry step) ──
    if step_by_id and not errors:
        entry = {
            s.id
            for s in steps
            if not any((s.id, p.port) in incoming for p in s.inputs) or s.type == "asset_input"
        }
        reachable: set[str] = set()
        stack = list(entry)
        while stack:
            node = stack.pop()
            if node in reachable:
                continue
            reachable.add(node)
            stack.extend(adjacency.get(node, set()))
        for i, step in enumerate(steps):
            if step.id not in reachable:
                errors.append(
                    _err(
                        "WF_UNREACHABLE_STEP",
                        f"/steps/{i}",
                        f"Step '{step.id}' is unreachable from any entry step",
                    )
                )

    return definition, errors


def validate_or_raise(raw: dict) -> WorkflowDefinition:
    """Validate and raise AppError(WF_VALIDATION_FAILED) with full details on failure."""
    definition, errors = validate_definition(raw)
    if errors:
        raise AppError(
            "WF_VALIDATION_FAILED",
            f"Workflow definition has {len(errors)} validation error(s)",
            422,
            details=errors,
        )
    assert definition is not None
    return definition


def derive_io_schemas(definition: WorkflowDefinition) -> tuple[list[dict], list[dict]]:
    """Derive cached input/output schemas for registry cards and run forms."""
    inputs = [
        {
            "key": i.key,
            "type": i.type,
            "label": i.label or i.key,
            "required": i.required,
            "default": i.default,
            "options": i.options,
        }
        for i in definition.inputs
    ]
    outputs = [{"key": o.key, "type": o.type} for o in definition.outputs]
    return inputs, outputs
