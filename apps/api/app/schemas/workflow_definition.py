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
# data: URIs and large base64 blobs are rejected — assets are ULID references.
# Media-type parameters (e.g. ;charset=utf-8) must not defeat the match, so
# any run of ;param segments between the subtype and ;base64, is consumed.
# The mediatype itself is optional per RFC 2397 ('data:;base64,' defaults to
# text/plain), so the type/subtype segment is optional too.
DATA_URI_RE = re.compile(
    r"data:([a-z0-9.+-]+/[a-z0-9.+-]+)?(;[^;,]{1,80})*;base64,", re.IGNORECASE
)
BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/=]{1024,}")
# NUL + C0/C1 control chars except tab (\x09) and newline (\x0a) — these
# crash asyncpg when stored into JSONB (UntranslatableCharacterError)
_CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")

MAX_STEPS = 50
MAX_EDGES = 150
MAX_STEP_CONFIG_BYTES = 16 * 1024
MAX_DEFINITION_BYTES = 256 * 1024
MAX_INPUTS = 20
MAX_OUTPUTS = 20


def _default_has_ctrl(v) -> bool:
    """True if any string in a parsed json default holds a control char.

    A json default arrives as an ESCAPED string in the definition (no literal
    control chars — WF_INVALID_CHARACTER cannot fire), but json.loads
    materializes real NULs that create_run's run-input screen then rejects on
    every default-driven run. Catch it at publish instead.
    """
    if isinstance(v, str):
        return bool(_CTRL_RE.search(v))
    if isinstance(v, dict):
        return any(_default_has_ctrl(k) or _default_has_ctrl(val) for k, val in v.items())
    if isinstance(v, list):
        return any(_default_has_ctrl(x) for x in v)
    return False


def _iter_cfg_strings(v):
    """Yield every raw string value in a nested config (keys excluded).

    Expression scanners must operate on raw strings, never json.dumps
    output: dumps escapes a newline inside {{ }} to the 2-char sequence
    \\n, which \\s* in EXPR_RE never matches — while the runtime renderer
    sees the raw newline and DOES resolve the reference. Scanner and
    renderer must see the same text. Mirrors _iter_strings in
    app/services/workflow_runtime.py.
    """
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for val in v.values():
            yield from _iter_cfg_strings(val)
    elif isinstance(v, (list, tuple)):
        for x in v:
            yield from _iter_cfg_strings(x)


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

    # NUL / C0-C1 control chars would be stored verbatim into a JSONB column
    # and crash asyncpg (UntranslatableCharacterError) at write time — a 500.
    # Reject as 422 (tab/newline allowed). Must scan the ACTUAL string values,
    # not json.dumps(raw): dumps escapes a NUL to a 6-char backslash sequence,
    # regex would never match. Same class of bug create_run/ComfyUI also guard.
    def _has_ctrl(v) -> bool:
        if isinstance(v, str):
            return bool(_CTRL_RE.search(v))
        if isinstance(v, dict):
            return any(_has_ctrl(k) or _has_ctrl(val) for k, val in v.items())
        if isinstance(v, list):
            return any(_has_ctrl(x) for x in v)
        return False

    if _has_ctrl(raw):
        errors.append(
            _err(
                "WF_INVALID_CHARACTER",
                "",
                "Definition contains NUL or control characters that are not allowed",
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

        # Output steps pair inputs[i] → outputs[i] POSITIONALLY at runtime
        # (input/output names can never match — WF_DUPLICATE_PORT spans both
        # lists). The pairing is the one data path that would otherwise skip
        # the COERCIBLE matrix, and a count mismatch silently emits None on
        # the unpaired output ports — both rejected here. Exception: a single
        # input fans out to every output port, which is always type-checked
        # pairwise below.
        if step.type == "output" and step.inputs and step.outputs:
            if len(step.inputs) != len(step.outputs) and len(step.inputs) != 1:
                errors.append(
                    _err(
                        "WF_OUTPUT_PORT_MISMATCH",
                        f"{ptr}/outputs",
                        f"Output step '{step.id}' has {len(step.inputs)} input ports "
                        f"and {len(step.outputs)} output ports — counts must match "
                        f"(or declare exactly one input to fan out)",
                    )
                )
            else:
                for j, out_port in enumerate(step.outputs):
                    in_port = step.inputs[j if len(step.inputs) > 1 else 0]
                    if out_port.type not in COERCIBLE.get(in_port.type, set()):
                        errors.append(
                            _err(
                                "WF_EDGE_TYPE_MISMATCH",
                                f"{ptr}/outputs/{j}",
                                f"Output step '{step.id}' pairs input "
                                f"'{in_port.port}' ({in_port.type}) with output "
                                f"'{out_port.port}' ({out_port.type}) — types are "
                                f"not coercible",
                            )
                        )

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
        # A default outside the option set bricks every default-driven run:
        # create_run applies the default, then rejects it as INVALID_INPUT_VALUE
        if (
            inp.type == "selection"
            and inp.options
            and inp.default is not None
            and inp.default not in inp.options
        ):
            errors.append(
                _err(
                    "WF_SELECTION_BAD_DEFAULT",
                    f"/inputs/{i}/default",
                    f"Selection input '{inp.key}' default must be one of its options",
                )
            )
        # Same bug class for every other type: create_run applies the default
        # then re-validates it, so a default that fails create_run's per-type
        # checks bricks every default-driven run. Mirror those checks here —
        # text/prompt ≤ 8000, asset refs ≤ 500, json parses to object/array,
        # stays ≤ 8000 chars stringified, and materializes no control chars
        # (an escaped \\u0000 in a json default becomes a REAL NUL after
        # json.loads and is rejected by the run-input ctrl screen).
        if inp.default is not None:
            bad_default: str | None = None
            if inp.type in ("text", "prompt") and len(inp.default) > 8000:
                bad_default = "text default exceeds the 8,000-character run-input limit"
            elif inp.type in ("image", "video", "audio", "reference_asset") and len(inp.default) > 500:
                bad_default = "asset-reference default exceeds the 500-character run-input limit"
            elif inp.type == "json":
                try:
                    parsed_default = _json.loads(inp.default)
                except (ValueError, TypeError):
                    parsed_default = None
                if not isinstance(parsed_default, (dict, list)):
                    bad_default = "json default must be a JSON object or array"
                elif len(str(parsed_default)) > 8000:
                    bad_default = "json default exceeds the 8,000-character run-input limit"
                elif _default_has_ctrl(parsed_default):
                    bad_default = "json default contains NUL or control characters"
            if bad_default is not None:
                errors.append(
                    _err(
                        "WF_INVALID_DEFAULT",
                        f"/inputs/{i}/default",
                        f"Input '{inp.key}': {bad_default}",
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

    # ── Fan-in: at most ONE edge per input port ──
    # The runtime resolves inputs per-edge in list order, so a second edge
    # into the same port would silently overwrite the first upstream's value.
    edge_index = {id(e): i for i, e in enumerate(edges)}
    for (to_step, to_port), port_edges in incoming.items():
        for extra in port_edges[1:]:
            errors.append(
                _err(
                    "WF_PORT_MULTIPLE_EDGES",
                    f"/edges/{edge_index[id(extra)]}",
                    f"Input port '{to_step}.{to_port}' has multiple incoming edges; "
                    "each input port accepts exactly one",
                )
            )

    # ── Moustache refs are DATA dependencies: derive implicit edges ──
    # A prompt_template referencing {{steps.X.outputs.Y}} must run after X —
    # the runtime renders unready refs as '', silently corrupting output.
    # Self-references can never be satisfied. Implicit edges join the Kahn
    # cycle check below so a template-induced cycle is still WF_GRAPH_CYCLE.
    # Scoped to prompt_template: it is the only step type whose config is
    # rendered at execution time (refs elsewhere are documentation-only).
    implicit_adjacency: dict[str, set[str]] = {s.id: set() for s in steps}
    step_ref_re = re.compile(r"^steps\.([a-z0-9_]+)\.outputs\.[a-z0-9_]+$")
    for i, step in enumerate(steps):
        if step.type != "prompt_template":
            continue
        # Scan RAW string values, not json.dumps — dumps escapes a newline
        # inside {{ }} to \n (2 chars), which \s* never matches, while the
        # runtime renderer sees the raw newline and DOES render the ref. The
        # scanner and renderer must agree or ordering edges silently vanish.
        for text in _iter_cfg_strings(step.config):
            for m in EXPR_RE.finditer(text):
                ref_m = step_ref_re.match(m.group(1))
                if ref_m is None:
                    continue
                ref_step = ref_m.group(1)
                if ref_step == step.id:
                    errors.append(
                        _err(
                            "WF_EXPR_SELF_REF",
                            f"/steps/{i}/config",
                            f"Step '{step.id}' references its own output "
                            f"'{{{{{m.group(1)}}}}}' — self-references can never resolve",
                        )
                    )
                elif ref_step in implicit_adjacency and step.id in implicit_adjacency:
                    implicit_adjacency[ref_step].add(step.id)

    # ── Cycle detection (Kahn) ──
    # Runs over explicit edges + implicit template-ref edges; a cycle only
    # closable through implicit edges is flagged meta.implicit=true.
    def _kahn_has_cycle(adj_maps: list[dict[str, set[str]]]) -> list[str]:
        """Return the steps stuck in a cycle ([] = acyclic) over merged adjacency."""
        indegree = {sid: 0 for sid in step_by_id}
        merged: dict[str, set[str]] = {sid: set() for sid in step_by_id}
        for adj in adj_maps:
            for src_id, targets in adj.items():
                if src_id in merged:
                    merged[src_id].update(t for t in targets if t in indegree)
        for targets in merged.values():
            for t in targets:
                indegree[t] += 1
        queue = [sid for sid, d in indegree.items() if d == 0]
        visited = 0
        while queue:
            node = queue.pop()
            visited += 1
            for t in merged[node]:
                indegree[t] -= 1
                if indegree[t] == 0:
                    queue.append(t)
        if visited < len(step_by_id):
            return sorted(sid for sid, d in indegree.items() if d > 0)
        return []

    if step_by_id:
        cycle_steps = _kahn_has_cycle([adjacency, implicit_adjacency])
        if cycle_steps:
            meta: dict = {"cycle_steps": cycle_steps}
            if not _kahn_has_cycle([adjacency]):
                meta["implicit"] = True  # cycle closes through a template ref
            errors.append(
                _err(
                    "WF_GRAPH_CYCLE",
                    "/edges",
                    f"Workflow graph contains a cycle involving: {', '.join(cycle_steps)}",
                    meta=meta,
                )
            )

    # ── Required inputs satisfied ──
    # A required input port must have an incoming EDGE — moustache refs never
    # feed input ports (they render inside the step config and are tracked
    # separately as implicit ordering edges above), so the check is
    # unconditional. asset_input steps are exempt: their ports are fed from
    # run inputs at execution time.
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
        # Raw string values, not json.dumps — see the implicit-edge scanner.
        for text in _iter_cfg_strings(step.config):
            for m in EXPR_RE.finditer(text):
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
    # Output keys follow the port grammar and must be unique — the runtime
    # collects outputs[out.key], so a duplicate silently overwrites its twin.
    output_keys: set[str] = set()
    for i, out in enumerate(definition.outputs):
        if not PORT_RE.match(out.key):
            errors.append(
                _err(
                    "WF_INVALID_OUTPUT_KEY",
                    f"/outputs/{i}/key",
                    f"Output key '{out.key}' must match ^[a-z][a-z0-9_]{{0,63}}$",
                )
            )
        if out.key in output_keys:
            errors.append(
                _err(
                    "WF_DUPLICATE_OUTPUT_KEY",
                    f"/outputs/{i}/key",
                    f"Duplicate output key '{out.key}'",
                )
            )
        output_keys.add(out.key)
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

    # NOTE: there is deliberately no "unreachable step" check. Every node of an
    # acyclic graph roots at an entry step (a step with no incoming edge IS an
    # entry step), a cyclic graph is already WF_GRAPH_CYCLE, and an input-starved
    # step is already WF_INPUT_UNSATISFIED — an inputless island step is VALID
    # (it simply runs as its own entry point).

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
