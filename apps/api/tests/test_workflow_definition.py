"""Unit tests for the workflow definition validator (ADR-010 D4).

These tests pin the validation contract: all error codes, JSON pointers,
size caps, coercion matrix, and the closed expression grammar.
"""

import pytest

from app.schemas.workflow_definition import (
    COERCIBLE,
    derive_io_schemas,
    validate_definition,
    validate_or_raise,
)


def _codes(errors):
    return {e["code"] for e in errors}


def _minimal_valid() -> dict:
    """A minimal valid two-step workflow: prompt_template → provider_action."""
    return {
        "schema_version": 1,
        "inputs": [
            {"key": "product_name", "type": "text", "required": True},
        ],
        "outputs": [
            {"key": "result_image", "type": "image", "from_step": "generate", "from_port": "result"},
        ],
        "steps": [
            {
                "id": "write_prompt",
                "type": "prompt_template",
                "name": "Build prompt",
                "config": {"template": "Photo of {{inputs.product_name}}"},
                "inputs": [],
                "outputs": [{"port": "prompt", "type": "prompt"}],
            },
            {
                "id": "generate",
                "type": "provider_action",
                "name": "Generate",
                "config": {"capability": "image_generation"},
                "inputs": [{"port": "prompt", "type": "prompt"}],
                "outputs": [{"port": "result", "type": "image"}],
            },
        ],
        "edges": [
            {
                "id": "e1",
                "from_step": "write_prompt",
                "from_port": "prompt",
                "to_step": "generate",
                "to_port": "prompt",
            },
        ],
        "ui": {"positions": {"write_prompt": [0, 0], "generate": [260, 0]}},
    }


# ── Happy path ────────────────────────────────────────────


def test_minimal_valid_definition():
    definition, errors = validate_definition(_minimal_valid())
    assert errors == []
    assert definition is not None
    assert len(definition.steps) == 2


def test_derive_io_schemas():
    definition, _ = validate_definition(_minimal_valid())
    inputs, outputs = derive_io_schemas(definition)
    assert inputs[0]["key"] == "product_name"
    assert inputs[0]["type"] == "text"
    assert outputs[0] == {"key": "result_image", "type": "image"}


# ── Step id rules ─────────────────────────────────────────


def test_invalid_step_id():
    d = _minimal_valid()
    d["steps"][0]["id"] = "Write-Prompt"  # uppercase + dash
    d["edges"] = []
    d["outputs"] = []
    _, errors = validate_definition(d)
    assert "WF_INVALID_STEP_ID" in _codes(errors)


def test_duplicate_step_id():
    d = _minimal_valid()
    d["steps"][1]["id"] = "write_prompt"
    d["edges"] = []
    d["outputs"] = []
    _, errors = validate_definition(d)
    assert "WF_DUPLICATE_STEP_ID" in _codes(errors)


# ── Graph rules ───────────────────────────────────────────


def test_cycle_detection_with_meta():
    d = _minimal_valid()
    # Make generate feed back into write_prompt (needs a text-ish edge)
    d["steps"][0]["inputs"] = [{"port": "feedback", "type": "prompt", "required": False}]
    d["edges"].append(
        {
            "id": "e2",
            "from_step": "generate",
            "from_port": "result",
            "to_step": "write_prompt",
            "to_port": "feedback",
        }
    )
    _, errors = validate_definition(d)
    codes = _codes(errors)
    assert "WF_GRAPH_CYCLE" in codes
    cycle_err = next(e for e in errors if e["code"] == "WF_GRAPH_CYCLE")
    # meta.cycle_steps names the cycle participants (REV-8)
    assert set(cycle_err["meta"]["cycle_steps"]) == {"write_prompt", "generate"}


def test_edge_unknown_step():
    d = _minimal_valid()
    d["edges"][0]["from_step"] = "ghost"
    _, errors = validate_definition(d)
    assert "WF_EDGE_UNKNOWN_STEP" in _codes(errors)


def test_edge_unknown_port():
    d = _minimal_valid()
    d["edges"][0]["from_port"] = "nonexistent"
    _, errors = validate_definition(d)
    assert "WF_EDGE_UNKNOWN_PORT" in _codes(errors)


def test_edge_type_mismatch():
    """image → prompt is not coercible; requires explicit transform."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "review",
            "type": "review_gate",
            "name": "QA",
            "config": {"due_days": 7},
            "inputs": [{"port": "subject", "type": "prompt"}],
            "outputs": [{"port": "decision", "type": "selection"}],
        }
    )
    d["edges"].append(
        {
            "id": "e3",
            "from_step": "generate",
            "from_port": "result",  # image
            "to_step": "review",
            "to_port": "subject",  # prompt — mismatch
        }
    )
    _, errors = validate_definition(d)
    mismatch = next(e for e in errors if e["code"] == "WF_EDGE_TYPE_MISMATCH")
    assert mismatch["meta"] == {"from_type": "image", "to_type": "prompt"}


def test_prompt_text_coercion_allowed():
    """prompt↔text is the ONLY automatic coercion besides identity."""
    assert "text" in COERCIBLE["prompt"]
    assert "prompt" in COERCIBLE["text"]
    assert "image" not in COERCIBLE["text"]
    assert COERCIBLE["image"] == {"image"}


def test_required_input_unsatisfied():
    d = _minimal_valid()
    d["edges"] = []  # generate.prompt now unfed
    d["outputs"] = []
    _, errors = validate_definition(d)
    assert "WF_INPUT_UNSATISFIED" in _codes(errors)


def test_inputless_island_step_is_valid():
    """An inputless island step IS valid (documented behavior): every node of
    an acyclic graph roots at an entry step, so a dedicated unreachable-step
    check can never fire — cyclic graphs are already WF_GRAPH_CYCLE and
    input-starved steps are already WF_INPUT_UNSATISFIED. The former
    WF_UNREACHABLE_STEP branch was dead code and has been removed."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "island",
            "type": "instruction",
            "name": "Island",
            "config": {"content": "do things"},
            "inputs": [],
            "outputs": [],
        }
    )
    _, errors = validate_definition(d)
    assert errors == []


# ── Expression grammar ────────────────────────────────────


def test_expr_unknown_reference():
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "Photo of {{inputs.nonexistent_key}}"
    _, errors = validate_definition(d)
    assert "WF_EXPR_INVALID" in _codes(errors)


def test_expr_step_output_reference_valid():
    d = _minimal_valid()
    # Referencing an upstream step output is allowed
    d["steps"][1]["config"]["capability"] = "image_generation"
    d["steps"].append(
        {
            "id": "notes",
            "type": "instruction",
            "name": "Notes",
            "config": {"content": "Used prompt: {{steps.write_prompt.outputs.prompt}}"},
            "inputs": [],
            "outputs": [],
        }
    )
    _, errors = validate_definition(d)
    assert errors == []


# ── Size caps ─────────────────────────────────────────────


def test_too_many_steps():
    d = _minimal_valid()
    d["edges"] = []
    d["outputs"] = []
    d["steps"] = [
        {
            "id": f"step_{i}",
            "type": "instruction",
            "name": f"S{i}",
            "config": {"content": "x"},
            "inputs": [],
            "outputs": [],
        }
        for i in range(51)
    ]
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_TOO_LARGE" and e["pointer"] == "/steps" for e in errors)


def test_definition_size_cap():
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "x" * 300_000
    result, errors = validate_definition(d)
    assert result is None
    assert errors[0]["code"] == "WF_TOO_LARGE"


def test_step_config_size_cap():
    d = _minimal_valid()
    d["edges"] = []
    d["outputs"] = []
    # instruction content ≤4000 passes Pydantic, so use transform params for bulk
    d["steps"] = [
        {
            "id": "big",
            "type": "transform",
            "name": "Big",
            "config": {"operation": "concat_text", "params": {"filler": "y" * 20_000}},
            "inputs": [],
            "outputs": [],
        }
    ]
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_TOO_LARGE" and "/config" in e["pointer"] for e in errors)


# ── Data URI rejection (D4) ───────────────────────────────


def test_data_uri_rejected():
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "data:image/png;base64,AAAA"
    _, errors = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" in _codes(errors)


def test_large_base64_blob_rejected():
    d = _minimal_valid()
    d["ui"]["blob"] = "A" * 2000  # looks like base64, ≥1024 chars
    _, errors = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" in _codes(errors)


# ── Config type validation ────────────────────────────────


def test_review_gate_due_days_bounds():
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "gate",
            "type": "review_gate",
            "name": "Gate",
            "config": {"due_days": 90},  # > 30
            "inputs": [],
            "outputs": [],
        }
    )
    _, errors = validate_definition(d)
    assert "WF_CONFIG_INVALID" in _codes(errors)


def test_transform_operation_whitelist():
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "evil",
            "type": "transform",
            "name": "Evil",
            "config": {"operation": "exec_shell", "params": {}},
            "inputs": [],
            "outputs": [],
        }
    )
    _, errors = validate_definition(d)
    assert "WF_CONFIG_INVALID" in _codes(errors)


def test_unknown_step_type_rejected():
    d = _minimal_valid()
    d["steps"][0]["type"] = "shell_command"
    result, errors = validate_definition(d)
    assert result is None
    assert "WF_SCHEMA_INVALID" in _codes(errors)


# ── Error accumulation ────────────────────────────────────


def test_all_errors_accumulated_in_one_pass():
    """Multiple independent errors must all be reported at once (Argo pattern)."""
    d = _minimal_valid()
    d["steps"][0]["id"] = "BAD-ID"
    d["edges"][0]["from_step"] = "ghost"
    d["steps"][1]["config"]["capability"] = "x" * 100  # config invalid (max 64)
    _, errors = validate_definition(d)
    codes = _codes(errors)
    assert "WF_INVALID_STEP_ID" in codes
    assert "WF_EDGE_UNKNOWN_STEP" in codes
    assert "WF_CONFIG_INVALID" in codes


def test_validate_or_raise_produces_app_error():
    from app.exceptions import AppError

    d = _minimal_valid()
    d["edges"][0]["from_step"] = "ghost"
    with pytest.raises(AppError) as exc:
        validate_or_raise(d)
    assert exc.value.code == "WF_VALIDATION_FAILED"
    assert exc.value.status_code == 422
    assert len(exc.value.details) >= 1
    assert all("pointer" in e for e in exc.value.details)


def test_selection_input_without_options_rejected():
    """A selection input with no options is unrunnable — every submitted
    value fails INVALID_INPUT_VALUE at create_run. Reject at publish time."""
    d = _minimal_valid()
    d["inputs"].append({"key": "pick", "type": "selection", "required": True})
    _, errors = validate_definition(d)
    assert "WF_SELECTION_NO_OPTIONS" in _codes(errors)

    # With options it validates
    d["inputs"][-1]["options"] = ["a", "b"]
    _, errors2 = validate_definition(d)
    assert "WF_SELECTION_NO_OPTIONS" not in _codes(errors2)


def test_control_characters_rejected():
    """NUL / C0 control chars would crash asyncpg on the JSONB write (a 500) —
    the validator must reject them as WF_INVALID_CHARACTER (422)."""
    d = _minimal_valid()
    d["inputs"][0]["label"] = "a" + chr(0) + "b"
    _, errors = validate_definition(d)
    assert "WF_INVALID_CHARACTER" in _codes(errors)
    # tab + newline stay allowed
    d2 = _minimal_valid()
    d2["inputs"][0]["label"] = "line1\nline2\tcol"
    _, errors2 = validate_definition(d2)
    assert "WF_INVALID_CHARACTER" not in _codes(errors2)


def test_nonfinite_float_in_definition_body_rejected():
    """R78: json.loads accepts bare NaN/Infinity tokens, the JSONB serializer
    re-emits them (allow_nan=True), and Postgres rejects them (22P02 → 500).
    R73 closed this class for provenance/config/limits/defaults but missed the
    definition body itself — reachable through the free-form ui block."""
    import json as _json

    d = _minimal_valid()
    d["ui"] = _json.loads('{"positions": {"a": [NaN, 0]}}')
    _, errors = validate_definition(d)
    assert "WF_INVALID_CHARACTER" in _codes(errors)
    # Infinity likewise
    d2 = _minimal_valid()
    d2["ui"] = _json.loads('{"zoom": Infinity}')
    _, errors2 = validate_definition(d2)
    assert "WF_INVALID_CHARACTER" in _codes(errors2)
    # ordinary finite floats and bools stay allowed
    d3 = _minimal_valid()
    d3["ui"] = {"positions": {"a": [1.5, 0]}, "snap": True}
    _, errors3 = validate_definition(d3)
    assert "WF_INVALID_CHARACTER" not in _codes(errors3)


def test_selection_default_must_be_in_options():
    """A selection input whose default is outside its options bricks every
    default-driven run (create_run applies then rejects it)."""
    d = _minimal_valid()
    d["inputs"].append(
        {"key": "pick", "type": "selection", "required": True, "options": ["a", "b"], "default": "z"}
    )
    _, errors = validate_definition(d)
    assert "WF_SELECTION_BAD_DEFAULT" in _codes(errors)
    d["inputs"][-1]["default"] = "a"
    _, errors2 = validate_definition(d)
    assert "WF_SELECTION_BAD_DEFAULT" not in _codes(errors2)


def test_json_default_must_parse_to_object_or_array():
    """A json-typed input default is a string (schema); if it doesn't parse to
    a dict/list, every default-driven run would fail INVALID_INPUT_VALUE at
    create_run — the exact bug class WF_SELECTION_BAD_DEFAULT fixed for
    selection inputs, recurring for json."""
    d = _minimal_valid()
    d["inputs"].append({"key": "cfg", "type": "json", "required": True, "default": "not-json"})
    _, errors = validate_definition(d)
    assert "WF_INVALID_DEFAULT" in _codes(errors)

    # A scalar parses but isn't an object/array — still rejected
    d["inputs"][-1]["default"] = "42"
    _, errors2 = validate_definition(d)
    assert "WF_INVALID_DEFAULT" in _codes(errors2)

    # A valid JSON object default passes
    d["inputs"][-1]["default"] = '{"a": 1}'
    _, errors3 = validate_definition(d)
    assert "WF_INVALID_DEFAULT" not in _codes(errors3)


def test_data_uri_with_media_type_params_rejected():
    """data: URIs with media-type parameters (;charset=utf-8) must not evade
    the D4 no-inline-data guarantee."""
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "data:text/plain;charset=utf-8;base64,SGVsbG8="
    _, errors = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" in _codes(errors)
    # Multiple parameters too
    d["steps"][0]["config"]["template"] = "data:text/plain;charset=utf-8;foo=bar;base64,SGVsbG8="
    _, errors2 = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" in _codes(errors2)


def test_fan_in_multiple_edges_into_same_port_rejected():
    """Two edges into the same input port validate to WF_PORT_MULTIPLE_EDGES —
    the runtime resolves per-edge in list order, so the second edge would
    silently overwrite the first upstream's value."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "second_prompt",
            "type": "prompt_template",
            "name": "Second prompt",
            "config": {"template": "Also {{inputs.product_name}}"},
            "inputs": [],
            "outputs": [{"port": "prompt", "type": "prompt"}],
        }
    )
    d["edges"].append(
        {
            "id": "e2",
            "from_step": "second_prompt",
            "from_port": "prompt",
            "to_step": "generate",
            "to_port": "prompt",  # same port as e1 — fan-in
        }
    )
    _, errors = validate_definition(d)
    fanin = next(e for e in errors if e["code"] == "WF_PORT_MULTIPLE_EDGES")
    # Pointer names the SECOND edge (the extra one)
    assert fanin["pointer"] == "/edges/1"

    # Single-edge shape stays valid
    _, errors2 = validate_definition(_minimal_valid())
    assert "WF_PORT_MULTIPLE_EDGES" not in _codes(errors2)


def test_output_key_grammar_and_duplicates():
    """Workflow output keys follow the port grammar and must be unique —
    duplicates silently overwrite each other in the final run outputs."""
    d = _minimal_valid()
    d["outputs"][0]["key"] = "WEIRD KEY!!"
    _, errors = validate_definition(d)
    assert "WF_INVALID_OUTPUT_KEY" in _codes(errors)

    d2 = _minimal_valid()
    d2["outputs"].append(
        {"key": "result_image", "type": "prompt", "from_step": "write_prompt", "from_port": "prompt"}
    )
    _, errors2 = validate_definition(d2)
    assert "WF_DUPLICATE_OUTPUT_KEY" in _codes(errors2)

    # Distinct valid keys pass
    d3 = _minimal_valid()
    d3["outputs"].append(
        {"key": "prompt_used", "type": "prompt", "from_step": "write_prompt", "from_port": "prompt"}
    )
    _, errors3 = validate_definition(d3)
    assert errors3 == []


def test_template_self_reference_rejected():
    """{{steps.SELF.outputs.*}} can never resolve — WF_EXPR_SELF_REF."""
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "Echo {{steps.write_prompt.outputs.prompt}}"
    _, errors = validate_definition(d)
    assert "WF_EXPR_SELF_REF" in _codes(errors)


def test_template_ref_cycle_detected_via_implicit_edge():
    """A moustache ref is a data dependency; a cycle only closable through it
    is still WF_GRAPH_CYCLE, flagged meta.implicit=true."""
    d = _minimal_valid()
    # write_prompt --edge--> generate; generate's output referenced back into
    # a second template that write_prompt's edge chain feeds… simplest cycle:
    # t1 template refs t2's output, t2 template refs t1's output (no edges).
    d["steps"] = [
        {
            "id": "t1",
            "type": "prompt_template",
            "name": "T1",
            "config": {"template": "use {{steps.t2.outputs.out}}"},
            "inputs": [],
            "outputs": [{"port": "out", "type": "prompt"}],
        },
        {
            "id": "t2",
            "type": "prompt_template",
            "name": "T2",
            "config": {"template": "use {{steps.t1.outputs.out}}"},
            "inputs": [],
            "outputs": [{"port": "out", "type": "prompt"}],
        },
    ]
    d["edges"] = []
    d["outputs"] = []
    _, errors = validate_definition(d)
    cycle = next(e for e in errors if e["code"] == "WF_GRAPH_CYCLE")
    assert set(cycle["meta"]["cycle_steps"]) == {"t1", "t2"}
    assert cycle["meta"]["implicit"] is True


def test_template_forward_ref_without_edge_is_valid_and_ordered():
    """A template referencing another step WITHOUT an edge stays valid (the
    endorsed authoring pattern) — ordering is enforced by the implicit edge,
    not rejected. The runtime test asserts execution order."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "summary",
            "type": "prompt_template",
            "name": "Summary",
            "config": {"template": "Prompt was: {{steps.write_prompt.outputs.prompt}}"},
            "inputs": [],
            "outputs": [{"port": "text", "type": "text"}],
        }
    )
    _, errors = validate_definition(d)
    assert errors == []


# ── Round-18 regressions: fixes of the round-15/16 fixes ──


def test_newline_inside_moustache_still_creates_implicit_edge():
    """A newline INSIDE {{ }} defeated the json.dumps-based scanner (dumps
    escapes it to the 2-char \\n which \\s* never matches) while the renderer
    resolved the ref on the raw template — ref rendered, no ordering edge.
    The scanner now walks raw strings: a self-ref written with a newline must
    be rejected exactly like the single-line form."""
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = (
        "use {{\n  steps.write_prompt.outputs.prompt\n}}"
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_EXPR_SELF_REF" for e in errors), errors


def test_newline_moustache_cycle_detected():
    """Template cycle written with newlines inside the braces must still be
    WF_GRAPH_CYCLE (implicit) — the raw-string scanner sees what the renderer
    sees."""
    d = _minimal_valid()
    # write_prompt references generate's output; generate already consumes
    # write_prompt via the explicit edge → cycle through the implicit edge
    d["steps"][0]["config"]["template"] = "x {{\nsteps.generate.outputs.result\n}}"
    _, errors = validate_definition(d)
    cycle = next((e for e in errors if e["code"] == "WF_GRAPH_CYCLE"), None)
    assert cycle is not None, errors
    assert cycle["meta"].get("implicit") is True


def test_output_step_port_count_mismatch_rejected():
    """Output steps pair inputs[i] → outputs[i] positionally at runtime; a
    count mismatch silently emitted None on unpaired output ports."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "deliver",
            "type": "output",
            "name": "Deliver",
            "config": {},
            "inputs": [
                {"port": "a", "type": "image"},
                {"port": "b", "type": "image", "required": False},
            ],
            "outputs": [
                {"port": "x", "type": "image"},
                {"port": "y", "type": "image"},
                {"port": "z", "type": "image"},
            ],
        }
    )
    d["edges"].append(
        {"id": "e_deliver", "from_step": "generate", "from_port": "result", "to_step": "deliver", "to_port": "a"}
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_OUTPUT_PORT_MISMATCH" for e in errors), errors


def test_output_step_positional_type_mismatch_rejected():
    """The positional pairing was the only data path skipping the COERCIBLE
    matrix: image input paired with a text output validated clean and flowed
    an image ref into a text-declared workflow output."""
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "deliver",
            "type": "output",
            "name": "Deliver",
            "config": {},
            "inputs": [{"port": "pic", "type": "image"}],
            "outputs": [{"port": "txt", "type": "text"}],
        }
    )
    d["edges"].append(
        {"id": "e_deliver", "from_step": "generate", "from_port": "result", "to_step": "deliver", "to_port": "pic"}
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_EDGE_TYPE_MISMATCH" for e in errors), errors


def test_output_step_matched_ports_still_valid():
    d = _minimal_valid()
    d["steps"].append(
        {
            "id": "deliver",
            "type": "output",
            "name": "Deliver",
            "config": {},
            "inputs": [{"port": "pic", "type": "image"}],
            "outputs": [{"port": "final", "type": "image"}],
        }
    )
    d["edges"].append(
        {"id": "e_deliver", "from_step": "generate", "from_port": "result", "to_step": "deliver", "to_port": "pic"}
    )
    _, errors = validate_definition(d)
    assert errors == []


def test_text_default_over_run_limit_rejected():
    """Publish-time guard for the whole default class: a text default beyond
    create_run's 8,000-char limit bricked every default-driven run."""
    d = _minimal_valid()
    d["inputs"].append(
        {"key": "blurb", "type": "text", "required": False, "default": "word " * 1800}
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_INVALID_DEFAULT" for e in errors), errors


def test_asset_default_over_ref_limit_rejected():
    d = _minimal_valid()
    d["inputs"].append(
        {"key": "ref_img", "type": "image", "required": False, "default": "x" * 600}
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_INVALID_DEFAULT" for e in errors), errors


def test_json_default_with_escaped_nul_rejected():
    """An escaped \\u0000 in a json default contains no literal control char
    (WF_INVALID_CHARACTER can't fire) and parses to a dict (the old check
    passed) — but json.loads materializes a real NUL that create_run's ctrl
    screen rejects on every default-driven run."""
    d = _minimal_valid()
    d["inputs"].append(
        {"key": "cfg", "type": "json", "required": False, "default": '{"a": "\\u0000"}'}
    )
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_INVALID_DEFAULT" for e in errors), errors


def test_omitted_mediatype_data_uri_rejected():
    """RFC 2397 allows 'data:;base64,' (mediatype defaults to text/plain) —
    the type/subtype-requiring regex missed it."""
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "data:;base64," + "A" * 64
    _, errors = validate_definition(d)
    assert any(e["code"] == "WF_DATA_URI_REJECTED" for e in errors), errors


def test_deeply_nested_config_no_recursion_error():
    """R20: json.loads accepts ~990-deep nesting (a 2KB payload passing every
    size cap) where recursive scanners RecursionError into a 500 — every
    walker on the definition path must be iterative. This exercises the ctrl
    scan, expression scanners, and default validation in one pass."""
    import json as _j

    deep_list = _j.loads("[" * 900 + '"x"' + "]" * 900)
    d = _minimal_valid()
    d["steps"][0]["config"]["deep"] = deep_list  # rides along in config
    # Must not raise — errors (if any) come back as structured entries
    _, errors = validate_definition(d)
    assert isinstance(errors, list)


def test_deep_json_default_no_recursion_error():

    d = _minimal_valid()
    # A deep-but-clean json default: parses fine; the ctrl scan must survive
    d["inputs"].append(
        {
            "key": "cfg",
            "type": "json",
            "required": False,
            "default": "[" * 900 + '"x"' + "]" * 900,
        }
    )
    _, errors = validate_definition(d)
    # Deep default exceeds the 8000-char stringified bound → WF_INVALID_DEFAULT
    # is acceptable; the point is NO RecursionError
    assert isinstance(errors, list)


def test_pathologically_deep_json_default_rejected_not_500():
    """R70: a FLAT json-default string ('['*9997+'1'+']'*9997) dodges the
    raw-definition depth gate (it is one scalar in the raw dict) but json.loads
    parses ~9997 levels deep. Two RecursionError doors → 500 at validate/publish:
    json.loads itself (its C recursion budget shrinks under FastAPI's deep
    middleware stack) and CPython's recursive container repr in len(str(...)).
    The raw-string-length cap (8000) short-circuits before either, and the
    parse catches RecursionError defensively — result is a clean
    WF_INVALID_DEFAULT, never a 500."""
    for depth in (9997, 2000, 500, 100):
        d = _minimal_valid()
        d["inputs"].append(
            {
                "key": "deep",
                "type": "json",
                "required": False,
                "default": "[" * depth + "1" + "]" * depth,
            }
        )
        # Must return structured errors, never raise RecursionError
        _, errors = validate_definition(d)
        assert any(e["code"] == "WF_INVALID_DEFAULT" for e in errors), (
            f"depth={depth}: {_codes(errors)}"
        )

    # Control: a normal shallow json default is still accepted
    ok = _minimal_valid()
    ok["inputs"].append(
        {"key": "cfg", "type": "json", "required": False, "default": '{"a": [1, 2, 3]}'}
    )
    _, ok_errors = validate_definition(ok)
    assert "WF_INVALID_DEFAULT" not in _codes(ok_errors), _codes(ok_errors)


def test_plain_data_uri_rejected():
    """R66: RFC 2397 allows non-base64 (URL-encoded/plain) payloads —
    'data:image/png,%89%50…' has no ';base64,' marker and '%' breaks the
    base64-blob charset, so ~96KB of inline media smuggled through the
    unbounded ui block. ADR-010's red line rejects data: URIs in any
    encoding; payloads ≥64 chars after the comma are rejected."""
    # URL-encoded payload in the ui block
    d = _minimal_valid()
    d["ui"]["note"] = "data:image/png," + "%89%50%4E%47" * 200
    _, errors = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" in _codes(errors)

    # plain-text payload in step config
    d2 = _minimal_valid()
    d2["steps"][0]["config"]["template"] = "data:text/html," + "A" * 100
    _, errors2 = validate_definition(d2)
    assert "WF_DATA_URI_REJECTED" in _codes(errors2)

    # omitted mediatype does not evade the match
    d3 = _minimal_valid()
    d3["ui"]["note"] = "data:," + "z" * 100
    _, errors3 = validate_definition(d3)
    assert "WF_DATA_URI_REJECTED" in _codes(errors3)


def test_whitespace_chunked_data_uri_rejected():
    """R78: DATA_URI_PLAIN_RE's {64,} needs an UNBROKEN payload run, so
    'data:image/png,' + 60-char %-encoded chunks joined by newlines/tabs
    (both JSONB-legal, exempt from _CTRL_RE) smuggled ~100KB of inline
    media past every matcher. A second scan on a whitespace-stripped copy
    (DATA_URI_STRIPPED_RE) closes the chunking evasion."""
    chunk = "%89%50%4E%47%0D%0A%1A%0A%00%00%00%0D%49%48%44%52%00%00%01%00"  # 60 chars
    for joiner in ("\n", "\t", " "):
        d = _minimal_valid()
        d["ui"]["note"] = "data:image/png," + joiner.join([chunk] * 200)
        _, errors = validate_definition(d)
        assert "WF_DATA_URI_REJECTED" in _codes(errors), f"joiner {joiner!r} evaded"

    # Prose containing a short data: mention followed by ordinary text keeps
    # validating — the stripped-scan payload charset breaks at prose chars.
    d2 = _minimal_valid()
    d2["ui"]["note"] = (
        "Reference assets by ID, e.g. data:text/plain,hello is rejected. "
        "Use the asset picker instead; uploads are stored as ULID references "
        "and resolved at run time by the executor, never inlined into the "
        "definition payload (see ADR-010 for the full rationale and limits)."
    )
    _, errors2 = validate_definition(d2)
    assert "WF_DATA_URI_REJECTED" not in _codes(errors2)


def test_short_data_uri_mention_still_valid():
    """Prose that merely MENTIONS a small data: URI (docs, instructions)
    must not be collateral damage of the plain-payload gate."""
    d = _minimal_valid()
    d["steps"][0]["config"]["template"] = "e.g. data:text/plain,hello {{inputs.topic}}"
    _, errors = validate_definition(d)
    assert "WF_DATA_URI_REJECTED" not in _codes(errors)

    d2 = _minimal_valid()
    d2["steps"][0]["config"]["template"] = "the data: URI scheme is rejected, use {{inputs.topic}}"
    _, errors2 = validate_definition(d2)
    assert "WF_DATA_URI_REJECTED" not in _codes(errors2)
