"""Workflow definition schema + full graph validator (ADR-010, D4).

Definitions are pure data over a CLOSED vocabulary of 7 step types and
8 I/O types. Validation accumulates ALL errors in one pass (Argo pattern),
each with a JSON pointer and machine code.

The no-code-execution guarantee lives here: no expressions beyond closed
moustache references, no data URIs, hard size caps, typed edges checked
against an explicit coercion matrix.
"""

import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
# the whole ;param section between the subtype and the ',' / ';base64,'
# terminator is consumed as ONE bounded non-comma segment (params cannot
# contain ',' per RFC 2397). One segment, not a repeated (;param)* group:
# the repeated group backtracks quadratically on adversarial ';x;x;x…'
# definitions — ~1.6s/request at the 256KB cap, a request-thread DoS (R78) —
# while a single [^,]{0,700} scan is linear and admits the same real URIs.
# The mediatype itself is optional per RFC 2397 ('data:;base64,' defaults to
# text/plain), so the type/subtype segment is optional too.
DATA_URI_RE = re.compile(r"data:([a-z0-9.+-]+/[a-z0-9.+-]+)?(;[^,]{0,700})?;base64,", re.IGNORECASE)
# Non-base64 data URIs (RFC 2397 allows URL-encoded payloads): '%89%50…'
# breaks BASE64_BLOB_RE's charset and carries no ';base64,' marker, so a
# percent-encoded payload smuggled ~96KB of inline media through the
# unbounded ui block (live-confirmed R66) — ADR-010's red line rejects
# data: URIs in ANY encoding. Require a ≥64-char payload after the comma
# so prose that merely MENTIONS a tiny data: URI stays valid.
DATA_URI_PLAIN_RE = re.compile(
    r"data:([a-z0-9.+-]+/[a-z0-9.+-]+)?(;[^,]{0,700})?,[^\s\"'\\]{64,}", re.IGNORECASE
)
BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/=]{1024,}")
# Whitespace-chunk evasion (R78): '{64,}' needs an UNBROKEN payload run, so
# "data:image/png," + 60-char %-encoded chunks joined by \n/\t (both
# JSONB-legal, exempt from _CTRL_RE) smuggled ~100KB past every matcher.
# A second scan on a whitespace-stripped copy closes it. Two deltas vs the
# unstripped regex: (1) threshold 256 not 64 — stripping glues prose too, and
# a real media payload needs kilobytes anyway; (2) the payload charset is
# encoded-data characters only (alnum % + / = . _ ~ -), so ordinary prose
# after a harmless data:-URI mention breaks the run at its first comma,
# apostrophe, paren, or non-ASCII character.
DATA_URI_STRIPPED_RE = re.compile(
    r"data:([a-z0-9.+-]+/[a-z0-9.+-]+)?(;[^,]{0,700})?,[A-Za-z0-9%+/=._~-]{256,}",
    re.IGNORECASE,
)
# The scan input is json.dumps output: literal spaces survive as-is, but
# newline/tab/CR appear as the 2-char escapes \n / \t / \r — strip both forms.
_WS_RE = re.compile(r"\s|\\[ntr]")
# NUL + C0/C1 control chars except tab (\x09) and newline (\x0a) — these
# crash asyncpg when stored into JSONB (UntranslatableCharacterError)
_CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")

MAX_STEPS = 50
MAX_EDGES = 150
MAX_STEP_CONFIG_BYTES = 16 * 1024
MAX_DEFINITION_BYTES = 256 * 1024
MAX_INPUTS = 20
MAX_OUTPUTS = 20
# json.loads parses far deeper than pydantic can serialize back (~400
# recursion cap) — a deep-nested block (ui, config) passes every structural
# check, stores fine, then PydanticSerializationError-500s EVERY subsequent
# detail read: the pack becomes permanently unreadable. Same class as
# create_run's run-input depth gate (_MAX_INPUT_DEPTH).
MAX_DEFINITION_DEPTH = 64


def _pg_jsonb_text_len(raw) -> int:
    """Estimate octet_length(value::jsonb::text) — the size the DB CHECK sees.

    R92d: Postgres jsonb normalizes numbers when rendering to text, expanding a
    float with a large-magnitude exponent (1e-300, 1e300) to its full decimal
    form (~300+ chars), so a payload can be small under Python json.dumps yet
    exceed the column's octet_length CHECK. Walk the structure counting each
    number at its worst-case jsonb::text width; structural characters and
    strings match json.dumps closely enough for a conservative bound.
    """
    import json as _json
    from decimal import Decimal

    def num_len(v) -> int:
        if isinstance(v, bool):
            return 4 if v else 5
        if isinstance(v, int):
            return len(str(v))
        # float: jsonb emits the shortest exact decimal, which for tiny/huge
        # magnitudes is the full non-exponent expansion. format(Decimal, 'f')
        # reproduces that; finite-ness is already enforced upstream.
        try:
            return len(format(Decimal(repr(v)), "f"))
        except Exception:
            return len(repr(v))

    total = 0
    stack = [raw]
    while stack:
        cur = stack.pop()
        if isinstance(cur, (bool, int, float)):
            total += num_len(cur)
        elif isinstance(cur, str):
            total += len(_json.dumps(cur, ensure_ascii=False).encode())
        elif cur is None:
            total += 4  # "null"
        elif isinstance(cur, dict):
            total += 2 + max(0, len(cur) - 1)
            for k, v in cur.items():
                total += len(_json.dumps(str(k), ensure_ascii=False).encode()) + 1
                stack.append(v)
        elif isinstance(cur, list):
            total += 2 + max(0, len(cur) - 1)
            stack.extend(cur)
        else:
            total += len(str(cur))
    return total


def _max_depth(v) -> int:
    """Iterative max nesting depth (recursion-free — that's the point)."""
    best = 1
    stack = [(v, 1)]
    while stack:
        cur, d = stack.pop()
        if d > best:
            best = d
        if isinstance(cur, dict):
            stack.extend((x, d + 1) for x in cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend((x, d + 1) for x in cur)
    return best


def _default_has_ctrl(v) -> bool:
    """True if any string in a parsed json default holds a control char, OR any
    float is non-finite (NaN/Infinity/-Infinity).

    A json default arrives as an ESCAPED string in the definition (no literal
    control chars — WF_INVALID_CHARACTER cannot fire), but json.loads
    materializes real NULs that create_run's run-input screen then rejects on
    every default-driven run. Catch it at publish instead. Same reasoning for
    non-finite floats (R73): json.loads('{"x": NaN}') yields float('nan'), which
    SQLAlchemy's default JSONB serializer re-emits as the literal `NaN` token
    → Postgres 22P02 → 500 on every default-driven run. bool is an int
    subclass, not float, so booleans are unaffected.

    ITERATIVE — json.loads parses deeper than the recursion limit allows a
    recursive scan to walk, so a deeply nested hostile default would
    RecursionError into a 500 at publish.
    """
    import math

    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            if _CTRL_RE.search(cur):
                return True
        elif isinstance(cur, float):
            if not math.isfinite(cur):
                return True
        elif isinstance(cur, dict):
            stack.extend(cur.keys())
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
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
    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            yield cur
        elif isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)


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
#
# extra="forbid" on EVERY config (R85): step config is stored verbatim in
# pack.definition → release.manifest → run.definition_snapshot AND served in
# the UNAUTHENTICATED registry preview. Without forbidding unknown keys, an
# author could smuggle a provider credential (e.g. {"capability": "...",
# "api_key": "sk-..."}) into a provider_action config — the same
# CREDENTIAL_IN_CONFIG footgun the ProviderConnection create path screens —
# and it would persist and leak publicly. Forbidding extras rejects any key
# outside the declared schema (WF_CONFIG_INVALID) at save/publish, so config
# can only ever hold the whitelisted non-sensitive fields.


class InstructionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(max_length=4000)


class PromptTemplateConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = Field(max_length=4000)


class AssetInputConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accept_types: list[Literal["image", "video", "audio", "reference_asset"]] = ["image"]


class TransformConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["crop", "resize", "concat_text", "select_field"]
    params: dict = {}


class ProviderActionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # min_length=1 (R83): an empty capability passed validation, then the
    # publish derivation skipped it (`if not key: continue`) so the install
    # capability gate saw no requirement and passed even with zero providers —
    # yet the runtime resolver matches capability_key == "" (never) and the
    # install binding-suggest read "" as "all capabilities". Three copies of
    # the rule disagreed on empty; forbidding it at the source (a definition
    # with an unset capability is WF_VALIDATION_FAILED at save/publish) is the
    # single fix. The editor's default provider_action seeds capability="", so
    # this also forces the author to pick one before saving.
    capability: str = Field(min_length=1, max_length=64)
    required_features: list[str] = []
    binding_mode: Literal["auto", "preferred", "pinned"] = "auto"
    pinned_offering_id: str | None = None


class ReviewGateConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instructions: str | None = Field(default=None, max_length=2000)
    due_days: int = Field(default=7, ge=1, le=30)


class OutputConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


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

    import json as _json

    # Depth cap FIRST — and before the size cap's json.dumps: json.loads
    # admits ~9997 nesting levels while the recursive json.dumps used for the
    # byte count dies ~1 level shallower, so a deep-but-parseable payload
    # would RecursionError-500 at the size check itself. _max_depth is
    # iterative (recursion-free), so it is the only safe first gate. Catches
    # the same small-but-deep brick (a 2KB 900-array payload passes the byte
    # cap, then 500s every subsequent read via pydantic's ~400 serializer
    # limit) as a clean 422.
    if _max_depth(raw) > MAX_DEFINITION_DEPTH:
        return None, [
            _err(
                "WF_TOO_DEEP",
                "",
                f"Definition is nested deeper than {MAX_DEFINITION_DEPTH} levels",
            )
        ]

    raw_bytes = len(_json.dumps(raw, ensure_ascii=False).encode())
    if raw_bytes > MAX_DEFINITION_BYTES:
        return None, [
            _err(
                "WF_TOO_LARGE",
                "",
                f"Definition is {raw_bytes} bytes; max {MAX_DEFINITION_BYTES}",
            )
        ]

    # R92d: the DB stores definition as JSONB with a CHECK on octet_length(
    # definition::text). Postgres normalizes numbers when rendering jsonb::text,
    # so a float with a large-magnitude exponent (e.g. 1e-300 → a ~302-char full
    # decimal expansion) is far wider on disk than in the Python json.dumps used
    # above. A payload that passes the byte cap here could therefore still blow
    # the DB CHECK (CheckViolationError / SQLSTATE 23514 — not an input-fault the
    # backstop maps) → unhandled 500. Re-measure with each number widened to its
    # worst-case jsonb::text form and gate on the SAME limit the column enforces.
    pg_bytes = _pg_jsonb_text_len(raw)
    if pg_bytes > MAX_DEFINITION_BYTES:
        return None, [
            _err(
                "WF_TOO_LARGE",
                "",
                f"Definition is {pg_bytes} bytes once stored; max {MAX_DEFINITION_BYTES}",
            )
        ]

    # data: URI / base64 blob rejection anywhere in the payload (D4).
    # Both encodings: ';base64,' marked AND plain/URL-encoded payloads.
    # ALSO scan a whitespace-stripped copy (R78) — closes the whitespace-
    # chunking evasion. BASE64_BLOB_RE (bare 1024-char run) must run against
    # BOTH flat AND flat_ws (R83): R78 wired the stripped scan to the data:-
    # prefixed matcher only, so a bare base64 blob chunked with JSONB-legal
    # newlines (no 'data:' prefix → DATA_URI_STRIPPED_RE never anchors) sailed
    # through. A blob is only inert-data, but ADR-010's inline-blob red line
    # rejects it in any framing.
    flat = _json.dumps(raw, ensure_ascii=False)
    flat_ws = _WS_RE.sub("", flat)
    if (
        DATA_URI_RE.search(flat)
        or DATA_URI_PLAIN_RE.search(flat)
        or DATA_URI_STRIPPED_RE.search(flat_ws)
        or BASE64_BLOB_RE.search(flat)
        or BASE64_BLOB_RE.search(flat_ws)
    ):
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
    # Also rejects non-finite floats (NaN/Infinity — R78): json.loads accepts
    # the bare tokens, the JSONB serializer re-emits them (allow_nan=True),
    # and Postgres rejects them (22P02) — a 500 through e.g. the ui block,
    # the one definition surface R73's sweep missed. bool is an int, never
    # a float, so True/False are unaffected.
    # Iterative — json.loads parses deeper than a recursive walk survives.
    def _has_ctrl(v) -> bool:
        stack = [v]
        while stack:
            cur = stack.pop()
            if isinstance(cur, str):
                if _CTRL_RE.search(cur):
                    return True
            elif isinstance(cur, float):
                if not math.isfinite(cur):
                    return True
            elif isinstance(cur, dict):
                stack.extend(cur.keys())
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
        return False

    if _has_ctrl(raw):
        errors.append(
            _err(
                "WF_INVALID_CHARACTER",
                "",
                "Definition contains NUL, control characters, or non-finite "
                "numbers (NaN/Infinity) that are not allowed",
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
            errors.append(
                _err("WF_DUPLICATE_STEP_ID", f"{ptr}/id", f"Duplicate step id '{step.id}'")
            )
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
        # (review_gate passthrough is checked AFTER edge processing — the
        # runtime's passthrough source is the first declared input with a
        # RESOLVED value, i.e. the first port fed by an edge, which is only
        # known once the incoming map exists. See the section below the
        # fan-in check.)

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
            errors.append(
                _err("WF_INVALID_PORT", f"/inputs/{i}/key", f"Invalid input key '{inp.key}'")
            )
        if inp.key in input_keys:
            errors.append(
                _err("WF_DUPLICATE_PORT", f"/inputs/{i}/key", f"Duplicate input '{inp.key}'")
            )
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
            elif (
                inp.type in ("image", "video", "audio", "reference_asset")
                and len(inp.default) > 500
            ):
                bad_default = "asset-reference default exceeds the 500-character run-input limit"
            elif inp.type == "json":
                # A flat json-default string dodges the raw-definition depth
                # gate (it is one scalar in the raw dict), but its CONTENT can
                # nest ~9997 levels. Two RecursionError doors, both → 500
                # (R70): (a) json.loads itself — the C parser's recursion
                # budget shrinks under FastAPI's deep middleware stack, so the
                # parse blows up live even though it survives a shallow local
                # call; (b) CPython's container repr in len(str(parsed)). Cap
                # the RAW string length first (a legit ≤8000-char default can
                # never nest past ~4000 levels, far under any parser limit),
                # then parse — catching RecursionError defensively.
                if len(inp.default) > 8000:
                    bad_default = "json default exceeds the 8,000-character run-input limit"
                else:
                    try:
                        parsed_default = _json.loads(inp.default)
                    except (ValueError, TypeError, RecursionError):
                        parsed_default = None
                        bad_default = "json default is not valid JSON"
                if bad_default is not None:
                    pass
                elif not isinstance(parsed_default, (dict, list)):
                    bad_default = "json default must be a JSON object or array"
                # Depth gate mirrors create_run's _MAX_INPUT_DEPTH (64) on the
                # PARSED value; _max_depth is iterative so it never recurses.
                elif _max_depth(parsed_default) > MAX_DEFINITION_DEPTH:
                    bad_default = (
                        f"json default is nested deeper than {MAX_DEFINITION_DEPTH} levels"
                    )
                elif len(str(parsed_default)) > 8000:
                    bad_default = "json default exceeds the 8,000-character run-input limit"
                elif _default_has_ctrl(parsed_default):
                    bad_default = (
                        "json default contains NUL/control characters or NaN/Infinity values"
                    )
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
            errors.append(
                _err("WF_DUPLICATE_EDGE_ID", f"{ptr}/id", f"Duplicate edge id '{edge.id}'")
            )
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

    # ── Review-gate passthrough typing ──
    # decide_review passes the FIRST declared input port WITH A RESOLVED
    # VALUE through to every non-`decision` output port. That passthrough
    # skips the edge coercion matrix exactly like an output step. Checking
    # only inputs[0] is WRONG when inputs[0] is optional and unconnected —
    # the runtime then sources the passthrough from the next CONNECTED port
    # (live-confirmed R66: optional image first + connected text second +
    # image 'passed' output validated, then fed text into an image
    # consumer). Model the runtime exactly: the passthrough source is the
    # first declared input that has an incoming edge (required ports always
    # do — enforced below), falling back to inputs[0] when nothing connects.
    for i, step in enumerate(steps):
        if step.type != "review_gate" or not step.inputs or not step.outputs:
            continue
        src_in = next(
            (p for p in step.inputs if (step.id, p.port) in incoming),
            step.inputs[0],
        )
        for j, out_port in enumerate(step.outputs):
            if out_port.port == "decision":
                continue  # decision is a synthesized selection, not passthrough
            if out_port.type not in COERCIBLE.get(src_in.type, set()):
                errors.append(
                    _err(
                        "WF_EDGE_TYPE_MISMATCH",
                        f"/steps/{i}/outputs/{j}",
                        f"Review gate '{step.id}' passes input "
                        f"'{src_in.port}' ({src_in.type}) through to output "
                        f"'{out_port.port}' ({out_port.type}) — types are not "
                        f"coercible",
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
    step_output_refs = {f"steps.{s.id}.outputs.{p.port}" for s in steps for p in s.outputs}
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
                _err(
                    "WF_EDGE_UNKNOWN_STEP",
                    f"/outputs/{i}/from_step",
                    f"Unknown step '{out.from_step}'",
                )
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
