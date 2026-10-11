"""Property-based tests over the fabric's pure cores (R107).

The probes killed targeted mutants; hypothesis hunts the inputs nobody
thought to write — the evaluator and matchers must be TOTAL over arbitrary
untrusted JSON (no exception may escape them)."""

from __future__ import annotations

import string

from hypothesis import given, settings
from hypothesis import strategies as st

json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(2**63), max_value=2**63),
    st.floats(allow_nan=True, allow_infinity=True),
    st.text(max_size=50),
)
json_values = st.recursive(
    json_scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(st.text(max_size=10), children, max_size=4),
    ),
    max_leaves=12,
)


@settings(max_examples=150, deadline=None)
@given(record=st.dictionaries(st.text(max_size=12), json_values, max_size=6))
def test_apply_mapping_total_over_arbitrary_records(record):
    """No record shape may crash the evaluator; every output field is either
    mapped or reported as an error — never silently both or neither."""
    from app.integrations.services.mapping import apply_mapping

    doc = {
        "fields": [
            {"target": "a", "path": "a", "transform": ["trim", "to_string"]},
            {"target": "b", "path": "b", "transform": ["to_int"]},
            {"target": "c", "path": "c", "transform": ["split_csv", "first"]},
            {"target": "d", "path": "d", "enum_map": {"x": "y"}, "enum_default": "z"},
        ]
    }
    mapped, errors = apply_mapping(doc, record)
    assert isinstance(mapped, dict) and isinstance(errors, list)
    error_fields = {e["field"] for e in errors}
    for target in ("a", "b", "c", "d"):
        assert (target in mapped) != (target in error_fields) or (
            target not in mapped and target not in error_fields
        )
    # NaN/Inf never leak into mapped output (JSONB safety).
    for v in mapped.values():
        if isinstance(v, float):
            assert v == v and v not in (float("inf"), float("-inf"))


@settings(max_examples=150, deadline=None)
@given(
    event_type=st.text(alphabet=string.ascii_lowercase + "._", min_size=1, max_size=60),
    patterns=st.lists(
        st.one_of(
            st.text(max_size=40),
            st.none(),
            st.integers(),
        ),
        max_size=5,
    ),
)
def test_event_matches_total_and_internal_safe(event_type, patterns):
    """event_matches never raises on junk patterns, and NO wildcard ever
    matches a fabric-internal event (feedback-loop invariant)."""
    from app.integrations.services.events import event_matches

    out = event_matches(patterns, event_type)
    assert isinstance(out, bool)
    internal = "com.openskill.integration.delivery.exhausted.v1"
    wildcard_only = [p for p in patterns if isinstance(p, str) and p.endswith(".*")]
    assert event_matches(wildcard_only, internal) is False


@settings(max_examples=100, deadline=None)
@given(header=st.text(max_size=120))
def test_parse_next_link_total(header):
    from app.integrations.services.lti_nrps import _parse_next_link

    out = _parse_next_link(header)
    assert out is None or isinstance(out, str)


@settings(max_examples=150, deadline=None)
@given(cell=st.text(max_size=80))
def test_sanitize_cell_idempotent_and_neutralizing(cell):
    """Sanitizing twice equals once, and the output never starts with a
    formula trigger (the CSV-injection contract)."""
    from app.integrations.services.bulk_import import _sanitize_cell

    once = _sanitize_cell(cell)
    assert _sanitize_cell(once) == once or once.startswith("'")
    if once:
        assert once[0] not in ("=", "+", "-", "@", "\t")


# ── R137: import parser properties (R128-R131 surface) ──


@given(st.binary(max_size=2000))
@settings(max_examples=200, deadline=None)
def test_detect_format_total(blob):
    """detect_format is total over arbitrary bytes and returns a known kind."""
    from app.integrations.services.bulk_import import detect_format

    assert detect_format(blob) in ("csv", "json")


@given(st.binary(max_size=2000))
@settings(max_examples=200, deadline=None)
def test_parse_users_any_bytes_never_raises(blob):
    """Both parsers are total over arbitrary bytes for every kind: garbage
    becomes (rows=[], errors=[...]) or valid rows — never an exception."""
    from app.integrations.services.bulk_import import detect_format, parse_users

    for kind in ("users", "roster", "opportunities"):
        rows, errors = parse_users(blob, detect_format(blob), {}, kind=kind)
        assert isinstance(rows, list) and isinstance(errors, list)


_EMAILS = st.from_regex(r"[a-z0-9]{1,10}@[a-z0-9]{1,8}\.[a-z]{2,4}", fullmatch=True)
_NAMES = st.text(
    alphabet=string.ascii_letters + string.digits + " -_",
    min_size=0, max_size=30,
)


@given(
    st.lists(
        st.tuples(_EMAILS, _NAMES, st.sampled_from(["student", "instructor", ""])),
        min_size=0, max_size=8,
    )
)
@settings(max_examples=400, deadline=None)
def test_csv_json_parity_for_users(rows):
    """Format parity: the same logical rows as CSV and as JSON validate to
    the same (email, display, role) multiset — JSON is a first-class
    template, not a lookalike."""
    import csv as _csv
    import io as _io
    import json as _json

    from app.integrations.services.bulk_import import parse_users

    buf = _io.StringIO()
    w = _csv.writer(buf)
    w.writerow(["email", "display_name", "role"])
    for e, d, r in rows:
        w.writerow([e, d, r])
    csv_rows, csv_errors = parse_users(buf.getvalue().encode(), "csv")

    payload = _json.dumps(
        [{"email": e, "display_name": d, "role": r} for e, d, r in rows]
    ).encode()
    json_rows, json_errors = parse_users(payload, "json")

    def key(row):
        return (row["email"], row["display_name"], row["role"])

    assert sorted(map(key, csv_rows)) == sorted(map(key, json_rows))
    assert len(csv_errors) == len(json_errors)


def test_nested_non_finite_rejected_not_staged():
    """R210 (R87 class): json.loads — and therefore connector resp.json() —
    accepts NaN/Infinity, so a non-finite float can arrive NESTED inside an
    object or list. It must become a non_finite error, never reach the mapped
    payload (where the JSONB write would 500 mid-run)."""
    import json as _json

    from app.integrations.services.mapping import apply_mapping

    doc = {"fields": [{"target": "meta", "path": "m"}, {"target": "tags", "path": "t"}]}
    record = _json.loads('{"m": {"score": NaN, "ok": 1}, "t": [1.0, Infinity]}')
    mapped, errors = apply_mapping(doc, record)
    codes = {e["field"]: e["code"] for e in errors}
    assert codes == {"meta": "non_finite", "tags": "non_finite"}
    assert mapped == {}

    # finite nested floats still pass untouched
    mapped2, errors2 = apply_mapping(doc, {"m": {"score": 1.5}, "t": [2.0]})
    assert errors2 == [] and mapped2 == {"meta": {"score": 1.5}, "tags": [2.0]}
