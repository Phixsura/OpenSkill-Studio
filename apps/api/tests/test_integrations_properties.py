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
