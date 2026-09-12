"""R428: workflow-runtime pure helpers — input safety, dependency scan,
templating and transforms. These gate 500-class crashes (control chars,
non-finite floats, deep nesting), scheduler ordering (template data deps),
and step execution semantics. All pure → fast, no DB.

Documented EQUIVALENT mutants (adjudicated):
- _max_depth L118 `d > deepest` >->>=: updating the running max to an equal
  value is idempotent — the returned depth is identical.
- _run_transform L1242/L1243 truncation bounds ([:10] separator, [:8000]
  concat result) ±1: a one-character bound change on already-bounded text
  is not observably different.
"""

import math
from types import SimpleNamespace

from app.services.workflow_runtime import (
    _iter_strings,
    _max_depth,
    _render_template,
    _render_value,
    _resolve_step_inputs,
    _run_transform,
    _template_ref_upstreams,
    _tenant_month_start,
    _upstream_ids,
    _values_have_ctrl,
)


def test_values_have_ctrl_r428():
    assert _values_have_ctrl("clean text") is False
    assert _values_have_ctrl("with\x00nul") is True
    assert _values_have_ctrl({"k": ["ok", "bad\x1f"]}) is True
    # control char hidden in a DICT KEY is caught (keys are walked)
    assert _values_have_ctrl({"bad\x07key": "ok"}) is True
    # inside a TUPLE (json.dumps would serialize as array) is caught
    assert _values_have_ctrl(("ok", "n\x0bo")) is True
    # non-finite floats are caught; bool (int subclass) and normal floats pass
    assert _values_have_ctrl(float("nan")) is True
    assert _values_have_ctrl(float("inf")) is True
    assert _values_have_ctrl(-math.inf) is True
    assert _values_have_ctrl({"n": 3.14, "ok": True, "z": 0}) is False
    # deep nesting must NOT recurse-crash (iterative)
    deep = []
    cur = deep
    for _ in range(2000):
        nxt = []
        cur.append(nxt)
        cur = nxt
    cur.append("bad\x00")
    assert _values_have_ctrl(deep) is True


def test_max_depth_r428():
    assert _max_depth("scalar") == 1
    assert _max_depth([]) == 1
    assert _max_depth([1, 2, 3]) == 2
    assert _max_depth({"a": {"b": {"c": 1}}}) == 4
    assert _max_depth({"a": [1, [2, [3]]]}) == 5  # dict→list→list→list→scalar
    # a tuple counts like a list
    assert _max_depth((1, (2, (3,)))) == 4


def test_template_ref_upstreams_and_deps_r428():
    # only prompt_template steps have template data deps
    non_tmpl = {"type": "transform", "config": {"template": "{{ steps.a.outputs.x }}"}}
    assert _template_ref_upstreams(non_tmpl) == set()

    tmpl = {
        "type": "prompt_template",
        "config": {"template": "Use {{ steps.gen.outputs.image }} and {{ inputs.topic }}"},
    }
    # a step ref is a dependency; an inputs ref is NOT an upstream step
    assert _template_ref_upstreams(tmpl) == {"gen"}

    # whitespace/newline inside the moustache still matches (renderer sees raw)
    tmpl2 = {
        "type": "prompt_template",
        "config": {"nested": {"t": "{{\n steps.foo.outputs.out \n}}"}},
    }
    assert _template_ref_upstreams(tmpl2) == {"foo"}

    # _upstream_ids unions edge upstreams with template deps
    steps = {"c": tmpl}
    edges = [{"from_step": "e1", "to_step": "c"}, {"from_step": "e2", "to_step": "other"}]
    assert _upstream_ids("c", steps, edges) == {"e1", "gen"}
    # a step with no edges/deps → empty
    assert _upstream_ids("missing", {}, []) == set()


def test_iter_strings_r428():
    got = set(_iter_strings({"a": "one", "b": ["two", {"c": "three"}], "n": 5}))
    assert got == {"one", "two", "three"}  # keys excluded, non-strings skipped


def test_render_value_r428():
    assert _render_value(None) == ""  # not "None"
    assert _render_value(True) == "true"  # JSON bool, not "True"
    assert _render_value(False) == "false"
    assert _render_value({"a": 1}) == '{"a": 1}'  # JSON, not repr
    assert _render_value([1, 2]) == "[1, 2]"
    assert _render_value("hi") == "hi"
    assert _render_value(42) == "42"


def test_render_template_r428():
    run = SimpleNamespace(inputs={"topic": "cats", "empty": None})
    step_runs = {"gen": SimpleNamespace(output={"image": "IMG"})}
    # inputs + step outputs render; None input → ''; unknown ref → ''
    out = _render_template(
        "T={{ inputs.topic }} I={{ steps.gen.outputs.image }} "
        "N={{ inputs.empty }} U={{ steps.none.outputs.x }}",
        run,
        step_runs,
    )
    assert out == "T=cats I=IMG N= U="
    # a step ref whose step_run has no output → '' (not a crash)
    sr_nooutput = {"gen": SimpleNamespace(output=None)}
    assert _render_template("{{ steps.gen.outputs.image }}", run, sr_nooutput) == ""
    # a MALFORMED steps ref missing the port (3 parts) → '' (kills the
    # `len==4 AND parts[2]=='outputs'` -> `or` mutant, which would index
    # parts[3] out of range on a 3-part ref)
    assert _render_template("X={{ steps.gen.outputs }}", run, step_runs) == "X="
    # a 4-part ref whose 3rd segment isn't 'outputs' → '' (not a wrong deref)
    assert _render_template("Y={{ steps.gen.inputs.image }}", run, step_runs) == "Y="


def test_resolve_step_inputs_r428():
    step = {"id": "s2", "type": "instruction"}
    edges = [
        {"from_step": "s1", "from_port": "out", "to_step": "s2", "to_port": "in"},
        {"from_step": "s1", "from_port": "x", "to_step": "other", "to_port": "y"},  # not s2
    ]
    step_runs = {"s1": SimpleNamespace(output={"out": "VAL", "x": "NO"})}
    run = SimpleNamespace(inputs={})
    assert _resolve_step_inputs(step, run, edges, step_runs) == {"in": "VAL"}

    # an edge whose source step has NO step_run yet (src is None) is skipped,
    # never dereferenced (kills the `src is not None AND output is not None`
    # -> `or` mutant, which would AttributeError on None.output)
    edges_missing = [
        {"from_step": "notrun", "from_port": "o", "to_step": "s2", "to_port": "in"},
    ]
    assert _resolve_step_inputs(step, run, edges_missing, step_runs) == {}
    # a source WITH a step_run but output=None is likewise skipped
    edges_noout = [
        {"from_step": "s3", "from_port": "o", "to_step": "s2", "to_port": "in"},
    ]
    assert _resolve_step_inputs(step, run, edges_noout, {"s3": SimpleNamespace(output=None)}) == {}

    # asset_input pulls its OUTPUT ports from run inputs by port name
    ai = {"id": "a", "type": "asset_input", "outputs": [{"port": "img"}, {"port": "missing"}]}
    run2 = SimpleNamespace(inputs={"img": "asset-1"})
    assert _resolve_step_inputs(ai, run2, [], {}) == {"img": "asset-1", "missing": None}


def test_run_transform_r428():
    # concat_text joins by DECLARED input-port order, skips None, applies sep
    step = {"inputs": [{"port": "a"}, {"port": "b"}], "outputs": [{"port": "result"}]}
    cfg = {"operation": "concat_text", "params": {"separator": " | "}}
    out = _run_transform(cfg, {"b": "second", "a": "first"}, step)
    assert out == {"result": "first | second"}  # declared order, not dict order
    # None values are skipped
    out2 = _run_transform(cfg, {"a": "only", "b": None}, step)
    assert out2 == {"result": "only"}

    # select_field: parses a JSON string source, returns the field
    sf = {"operation": "select_field", "params": {"field": "name"}}
    step_sf = {"inputs": [{"port": "a"}], "outputs": [{"port": "r"}]}
    assert _run_transform(sf, {"a": '{"name": "Ada"}'}, step_sf) == {"r": "Ada"}
    assert _run_transform(sf, {"a": {"name": "Ada"}}, step_sf) == {"r": "Ada"}
    # a non-dict/invalid-json source → None
    assert _run_transform(sf, {"a": "not json"}, step_sf) == {"r": None}
    assert _run_transform(sf, {}, step_sf) == {"r": None}

    # unknown op → pass-through first value + records operation/params
    passthru = _run_transform({"operation": "crop", "params": {"w": 10}}, {"a": "img"}, step_sf)
    assert passthru == {"r": "img", "_operation": "crop", "_params": {"w": 10}}


def test_tenant_month_start_r428():
    from datetime import UTC, datetime

    # a UTC+13 tenant at 2026-03-01T05:00Z is already 2026-03-01 18:00 local —
    # same month; month start is 2026-02-28T11:00Z (Mar 1 00:00 +13)
    at = datetime(2026, 3, 1, 5, 0, tzinfo=UTC)
    ms = _tenant_month_start("Pacific/Auckland", at)  # +13 (DST) / +12
    assert ms.tzinfo is not None
    # the resulting instant, viewed in the tenant tz, is the 1st at 00:00
    from zoneinfo import ZoneInfo

    local = ms.astimezone(ZoneInfo("Pacific/Auckland"))
    assert (local.day, local.hour, local.minute) == (1, 0, 0)
    # a bogus tz falls back to UTC month start
    ms_utc = _tenant_month_start("Not/AZone", at)
    assert (ms_utc.day, ms_utc.hour) == (1, 0)
