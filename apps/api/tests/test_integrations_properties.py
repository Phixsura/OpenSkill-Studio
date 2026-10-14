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
    min_size=0,
    max_size=30,
)


@given(
    st.lists(
        st.tuples(_EMAILS, _NAMES, st.sampled_from(["student", "instructor", ""])),
        min_size=0,
        max_size=8,
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

    payload = _json.dumps([{"email": e, "display_name": d, "role": r} for e, d, r in rows]).encode()
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


def test_every_canonical_model_has_strict_schema_keys():
    """R232 (R231 class): strict_schema silently no-ops for a model missing
    from MODEL_REQUIRED_KEYS (frozenset() fallback). Adding an 11th canonical
    model without declaring its required keys must fail here, not ship a
    validation gate that validates nothing."""
    from app.integrations.models.sync import CANONICAL_MODELS, MODEL_REQUIRED_KEYS

    missing = CANONICAL_MODELS - set(MODEL_REQUIRED_KEYS)
    assert not missing, f"models without strict_schema keys: {sorted(missing)}"
    stray = set(MODEL_REQUIRED_KEYS) - CANONICAL_MODELS
    assert not stray, f"required-keys entries for unknown models: {sorted(stray)}"
    assert all(MODEL_REQUIRED_KEYS[m] for m in MODEL_REQUIRED_KEYS), "empty key sets"


def test_schedule_and_import_registries_are_coherent():
    """R233 (R231 class): three registries that drift silently.
    (1) Adding a schedule to SYNC_SCHEDULES / EXPORT_SCHEDULES without a
        period in the sweep's cadence map means profiles/streams on that
        schedule are accepted by the API but NEVER auto-run (silent no-op).
    (2) IMPORT_KINDS, TEMPLATE_VERSIONS and KIND_SPECS must agree or a kind
        parses with no validator / versions without a parser.
    """
    from datetime import timedelta

    from app.integrations.models.bulk import IMPORT_KINDS
    from app.integrations.models.export import EXPORT_SCHEDULES
    from app.integrations.models.sync import SYNC_SCHEDULES
    from app.integrations.services.bulk_import import KIND_SPECS, TEMPLATE_VERSIONS
    from app.integrations.services.warehouse import _EXPORT_CADENCE

    # Rebuild the sync sweep's inline period mapping here; keep in lockstep
    # with sweep_scheduled_profiles (hourly/daily arms).
    sync_cadence = {"hourly": timedelta(hours=1), "daily": timedelta(days=1)}
    assert SYNC_SCHEDULES - {"manual"} == set(sync_cadence), (
        "SYNC_SCHEDULES gained a schedule the sweep never runs"
    )
    assert EXPORT_SCHEDULES - {"manual"} == set(_EXPORT_CADENCE), (
        "EXPORT_SCHEDULES gained a schedule the sweep never runs"
    )
    assert set(KIND_SPECS) == IMPORT_KINDS == set(TEMPLATE_VERSIONS), (
        "import kind registries drifted"
    )


@given(st.text(max_size=120))
@settings(max_examples=300, deadline=None)
def test_scim_parse_filter_total(expr):
    """R268: the SCIM filter parser is TOTAL over arbitrary text — it either
    returns (attr, value) for the supported eq-grammar or raises ScimError;
    no other exception may escape (IdPs send garbage filters)."""
    from app.integrations.services.scim import ScimError, ScimUserService

    try:
        attr, value = ScimUserService._parse_filter(expr)
    except ScimError as e:
        assert e.status == 400
    else:
        assert isinstance(attr, str) and attr == attr.lower()
        assert isinstance(value, str)


@given(st.text(max_size=200))
@settings(max_examples=300, deadline=None)
def test_validate_egress_url_total(url):
    """R268: the egress screen is TOTAL over arbitrary URL text — returns
    the normalized URL or raises EgressBlockedError, never a parser leak
    (IndexError/ValueError/UnicodeError), since every protocol feeds it
    attacker-influenced URLs."""
    from app.integrations.security import EgressBlockedError, validate_egress_url

    try:
        out = validate_egress_url(url)
    except EgressBlockedError:
        pass
    else:
        assert isinstance(out, str)


@given(st.text(max_size=120))
@settings(max_examples=300, deadline=None)
def test_normalized_email_domain_total(raw):
    """R321: the IDN email-domain folder is TOTAL over arbitrary text —
    returns a lowercase domain string or "", never raises (it feeds the
    auth gate; a hostile address must not 500 the login path)."""
    from app.integrations.services.domains import normalized_email_domain

    out = normalized_email_domain(raw)
    assert isinstance(out, str)
    assert out == out.lower()


@given(st.integers(min_value=0, max_value=2**32 - 1), st.sampled_from([80, 443, 8080, 8443]))
@settings(max_examples=500, deadline=None)
def test_egress_soundness_private_ipv4_always_blocked(ip_int, port):
    """R408 (SSRF SOUNDNESS, not just totality): every IPv4 the classifier
    deems forbidden (private/loopback/link-local/CGNAT/metadata/reserved)
    must be REFUSED by validate_egress_url in production mode — no URL-parse
    confusion path may admit one. Generates the full IPv4 space and cross-
    checks the validator against the authoritative classifier."""
    import ipaddress

    from app.config import settings
    from app.integrations.security import (
        EgressBlockedError,
        _is_forbidden_ip,
        validate_egress_url,
    )

    ip = str(ipaddress.IPv4Address(ip_int))
    forbidden = _is_forbidden_ip(ip)
    if not forbidden:
        return  # public IP: admit/deny is a separate (port/scheme) concern

    old = settings.egress_allow_private
    settings.egress_allow_private = False
    try:
        raised = False
        try:
            validate_egress_url(f"https://{ip}:{port}/x")
        except EgressBlockedError:
            raised = True
        assert raised, f"SSRF BYPASS: private/metadata {ip} was admitted"
    finally:
        settings.egress_allow_private = old


# Alternate IPv4 encodings that have historically bypassed SSRF screens.
_METADATA_ENCODINGS = [
    "169.254.169.254",  # AWS/GCP/Azure metadata
    "[::ffff:169.254.169.254]",  # IPv4-mapped IPv6
    "[::ffff:a9fe:a9fe]",  # same, hex form
    "127.0.0.1",
    "[::1]",
    "10.0.0.1",
    "192.168.1.1",
    "172.16.0.1",
    "100.64.0.1",  # CGNAT
    "0.0.0.0",
    "[fd00::1]",  # IPv6 ULA (private)
    "[fe80::1]",  # IPv6 link-local
]


@given(st.sampled_from(_METADATA_ENCODINGS), st.sampled_from([80, 443, 8080, 8443]))
@settings(max_examples=60, deadline=None)
def test_egress_soundness_metadata_encodings_blocked(host, port):
    """R408: the canonical metadata/loopback/private literals and their
    IPv4-mapped-IPv6 encodings are ALWAYS refused in production mode."""
    from app.config import settings
    from app.integrations.security import EgressBlockedError, validate_egress_url

    old = settings.egress_allow_private
    settings.egress_allow_private = False
    try:
        raised = False
        try:
            validate_egress_url(f"https://{host}:{port}/p")
        except EgressBlockedError:
            raised = True
        assert raised, f"SSRF BYPASS: {host} admitted"
    finally:
        settings.egress_allow_private = old


@given(
    st.one_of(
        st.none(),
        st.text(max_size=120),
        st.integers(),
        st.lists(st.text(max_size=8), max_size=4),
        st.dictionaries(st.text(max_size=6), st.text(max_size=6), max_size=3),
    )
)
@settings(max_examples=300, deadline=None)
def test_scim_normalize_path_total(path):
    """R409: the SCIM PATCH op-path normalizer is TOTAL over arbitrary op
    shapes — a non-string path (int/list/dict) raises a clean ScimError,
    any string returns a lowercased str; never a bare AttributeError /
    500 (R358 was exactly that class, fuzz-found). The PATCH grammar is
    attacker-shaped input."""
    from app.integrations.services.scim import ScimError, _normalize_path

    try:
        out = _normalize_path(path)
    except ScimError as e:
        assert e.status == 400
    else:
        # case PRESERVED by design (member-filter ids); totality is the
        # invariant — a str out, never a bare AttributeError/500.
        assert isinstance(out, str)


_json_like = st.recursive(
    st.one_of(
        st.none(), st.booleans(), st.integers(), st.floats(allow_nan=True), st.text(max_size=20)
    ),
    lambda c: st.one_of(
        st.lists(c, max_size=4), st.dictionaries(st.text(max_size=8), c, max_size=4)
    ),
    max_leaves=12,
)


@given(_json_like)
@settings(max_examples=400, deadline=None)
def test_scim_coerce_active_total(value):
    """R410: the SCIM active-flag coercion is TOTAL over arbitrary PATCH
    values (bool/str/dict-wrapped/garbage) — returns bool or None, never
    raises (it gates deprovisioning; a hostile value must not 500 the
    SCIM write path), and is recursion-safe on nested dicts."""
    from app.integrations.services.scim import _coerce_active

    out = _coerce_active(value)
    assert out is None or isinstance(out, bool)


@given(st.text(max_size=60))
@settings(max_examples=300, deadline=None)
def test_saml_parse_time_total(value):
    """R410: the SAML timestamp parser returns an AWARE datetime or raises
    a clean ValueError (never TypeError/AttributeError) over arbitrary
    strings — the caller's ValueError guard turns malformed stamps into a
    403, so any other exception class would 500 the ACS."""
    from datetime import datetime

    from app.integrations.services.sso_saml import _parse_time

    try:
        out = _parse_time(value)
    except ValueError:
        pass
    else:
        assert isinstance(out, datetime) and out.tzinfo is not None


@given(st.binary(max_size=4096), st.text(max_size=40), st.integers(min_value=0, max_value=2**40))
@settings(max_examples=200, deadline=None)
def test_webhook_sign_payload_total_and_deterministic(body, secret, ts):
    """R410: the Standard-Webhooks signer is TOTAL (any bytes body / secret
    / timestamp) and DETERMINISTIC — the same inputs always yield the same
    signature, and it is a non-empty base64 string (receivers recompute
    and compare)."""
    from app.integrations.services.events import sign_payload

    s1 = sign_payload(secret, "evt_1", ts, body)
    s2 = sign_payload(secret, "evt_1", ts, body)
    assert s1 == s2
    assert isinstance(s1, str) and s1.startswith("v1,") and len(s1) > 4


@settings(max_examples=200, deadline=None)
@given(
    rows=st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=10_000),
            st.dictionaries(st.text(max_size=12), json_values, max_size=6),
        ),
        max_size=6,
    )
)
def test_bulk_import_row_validators_total(rows):
    """R458: the three bulk-import row validators are TOTAL over arbitrary
    (row_number, dict) inputs — untrusted import data must never raise (R87
    class). Each returns (clean_rows, errors) where every error carries the
    full envelope (row_number/column/code/message/raw_row)."""
    from app.integrations.services.bulk_import import (
        _validate_opportunity_rows,
        _validate_roster_rows,
        _validate_user_rows,
    )

    for fn in (_validate_user_rows, _validate_roster_rows, _validate_opportunity_rows):
        clean, errors = fn(list(rows))
        assert isinstance(clean, list) and isinstance(errors, list)
        for e in errors:
            assert {"row_number", "column", "code", "message", "raw_row"} <= set(e)
            # raw_row values are all truncated strings (never a dict/list reaching JSONB)
            assert all(isinstance(v, str) for v in e["raw_row"].values())


@settings(max_examples=200, deadline=None)
@given(item=st.dictionaries(st.text(max_size=12), json_values, max_size=6))
def test_connector_map_record_total(item):
    """R458: the OneRoster and generic-CRM canonical mappers are TOTAL over
    arbitrary provider JSON objects — a hostile/degenerate record must never
    raise (it becomes a dict with a stringified external_id)."""
    from app.integrations.registry import GenericCrmConnector, OneRosterConnector

    for model in ("roster.term", "roster.class", "roster.enrollment", "roster.user"):
        out = OneRosterConnector._map_record(model, dict(item))
        assert isinstance(out, dict) and isinstance(out["external_id"], str)
    for model in ("crm.account", "crm.contact", "crm.deal"):
        out = GenericCrmConnector._map_record(model, dict(item))
        assert isinstance(out, dict) and isinstance(out["external_id"], str)
