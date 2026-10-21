"""R609: property proofs for security-relevant pure helpers (DB-free).

The SSRF classifier gets a DUAL-IMPLEMENTATION check: the test declares the
forbidden address space as an explicit CIDR union (reading the RFCs, not the
code) and compares the production flag-based classifier against it across
randomly sampled 32-bit/128-bit address space — a flag-semantics surprise in
a future Python version fails here. The protocol parsers get hostile-input
totality (never raise, bounded output).
"""

import ipaddress

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.integrations.security import _is_forbidden_ip

# The forbidden v4 space, declared INDEPENDENTLY from the implementation
# (RFC 1918/1122/3927/5771/1112/6598/919 + unspecified):
_FORBIDDEN_V4 = [
    ipaddress.ip_network(c)
    for c in (
        "0.0.0.0/8",  # unspecified / "this" network (is_unspecified + reserved-ish)
        "10.0.0.0/8",
        "100.64.0.0/10",  # CGNAT
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.0.0.0/24",  # IETF protocol assignments (is_private)
        "192.0.2.0/24",  # TEST-NET-1 (is_private per Python)
        "192.168.0.0/16",
        "198.18.0.0/15",  # benchmarking (is_private per Python)
        "198.51.100.0/24",  # TEST-NET-2
        "203.0.113.0/24",  # TEST-NET-3
        "224.0.0.0/4",  # multicast
        "240.0.0.0/4",  # reserved (incl. 255.255.255.255)
    )
]


def _reference_forbidden_v4(ip: ipaddress.IPv4Address) -> bool:
    return any(ip in net for net in _FORBIDDEN_V4)


@settings(max_examples=2000, deadline=None)
@given(st.integers(min_value=0, max_value=2**32 - 1))
def test_v4_classifier_matches_rfc_reference(u32):
    ip = ipaddress.IPv4Address(u32)
    assert _is_forbidden_ip(str(ip)) == _reference_forbidden_v4(ip), str(ip)


@settings(max_examples=500, deadline=None)
@given(st.integers(min_value=0, max_value=2**128 - 1))
def test_v6_classifier_never_raises_and_blocks_mapped_private(u128):
    ip = ipaddress.IPv6Address(u128)
    verdict = _is_forbidden_ip(str(ip))  # must never raise
    assert isinstance(verdict, bool)
    # IPv4-mapped addresses must agree with the v4 verdict of the payload.
    if ip.ipv4_mapped is not None:
        assert verdict == _reference_forbidden_v4(ip.ipv4_mapped), str(ip)


@settings(max_examples=500, deadline=None)
@given(st.text(max_size=200))
def test_classifier_total_over_garbage(s):
    # Unparseable input is FORBIDDEN (fail closed), never an exception.
    v = _is_forbidden_ip(s)
    assert isinstance(v, bool)
    try:
        ipaddress.ip_address(s)
    except ValueError:
        assert v is True


@settings(max_examples=500, deadline=None)
@given(st.one_of(st.none(), st.text(max_size=300)))
def test_nrps_next_link_parser_total(header):
    from app.integrations.services.lti_nrps import _parse_next_link

    out = _parse_next_link(header)
    assert out is None or isinstance(out, str)


def test_nrps_next_link_rejects_malformed_segment():
    """R640: a segment not wrapped in <...> must be SKIPPED, not partially
    parsed into a garbage URL (the Or→And mutant would return '<junk')."""
    from app.integrations.services.lti_nrps import _parse_next_link

    assert _parse_next_link('x<junk>; rel="next"') is None
    assert _parse_next_link('<https://ok/next>; rel="next"') == "https://ok/next"


@settings(max_examples=500, deadline=None)
@given(st.text(max_size=120))
def test_saml_time_parser_contract(s):
    """_parse_time's contract: an AWARE datetime, or exactly ValueError
    (every caller guards ValueError and converts to a typed 403). Any OTHER
    exception type — or a naive result — escapes the guards as a 500
    (R609 found the SLO path re-deriving a naive datetime that blew up as
    TypeError past the guard)."""
    from app.integrations.services.sso_saml import _parse_time

    try:
        out = _parse_time(s)
    except ValueError:
        return  # the guarded contract
    import datetime as _dt

    assert isinstance(out, _dt.datetime) and out.tzinfo is not None


@settings(max_examples=500, deadline=None)
@given(st.one_of(st.none(), st.text(max_size=300)))
def test_scim_path_normalizer_total(p):
    from app.integrations.services.scim import _normalize_path

    out = _normalize_path(p)
    assert isinstance(out, str)


# ── R636: eco fetcher resolve-pin (DNS-rebinding defense) ──


@pytest.mark.asyncio
async def test_eco_fetcher_blocks_rebound_dns(monkeypatch):
    """A registry whose DNS flips to a private IP between validation and
    fetch must be refused AT DIAL TIME (the R636 pin), not only at the
    earlier validate_external_url check."""
    import socket as _socket

    from app.ecosystem.security import EcoSecurityError
    from app.ecosystem.services import sync as eco_sync

    def rebound(host, port, proto=0):
        return [(2, 1, 6, "", ("10.66.0.1", port))]

    monkeypatch.setattr(_socket, "getaddrinfo", rebound)
    with pytest.raises(EcoSecurityError):
        await eco_sync._default_fetcher(
            "https://registry.example.com/models.json",
            etag=None,
            last_modified=None,
            timeout=5,
            max_bytes=1024,
        )


@pytest.mark.asyncio
async def test_eco_fetcher_pins_ip_and_sends_host_header(monkeypatch):
    """The pinned dial must hit the RESOLVED ip while presenting the original
    hostname in the Host header (so vhosted registries still route)."""
    import asyncio as _aio
    import socket as _socket

    from app.ecosystem.services import sync as eco_sync

    seen = {}

    async def handle(reader, writer):
        data = await reader.read(2048)
        head = data.decode(errors="replace")
        seen["host"] = next(
            (ln.split(":", 1)[1].strip() for ln in head.splitlines() if ln.lower().startswith("host:")),
            "",
        )
        body = b'{"ok": true}'
        writer.write(
            b"HTTP/1.1 200 OK\r\ncontent-type: application/json\r\ncontent-length: "
            + str(len(body)).encode()
            + b"\r\nconnection: close\r\n\r\n"
            + body
        )
        await writer.drain()
        writer.close()

    server = await _aio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]

    real_gai = _socket.getaddrinfo

    def to_local(host, p, proto=0):
        if host == "vhost.example.com":
            return [(2, 1, 6, "", ("127.0.0.1", p))]
        return real_gai(host, p, proto=proto)

    monkeypatch.setattr(_socket, "getaddrinfo", to_local)
    # loopback is normally forbidden — allow it for THIS plumbing test only
    monkeypatch.setattr(eco_sync, "_pin_forbidden", lambda a: False, raising=False)
    from app.ecosystem import security as eco_sec

    monkeypatch.setattr(eco_sec, "_is_forbidden_ip", lambda a: False)

    try:
        res = await eco_sync._default_fetcher(
            f"http://vhost.example.com:{port}/models.json",
            etag=None,
            last_modified=None,
            timeout=5,
            max_bytes=4096,
        )
    finally:
        server.close()
        await server.wait_closed()
    assert res.status_code == 200 and res.body == b'{"ok": true}'
    assert seen["host"] == f"vhost.example.com:{port}"


# ── R651: mapping.py boundary pins (13 mutation survivors, all unpinned edges)


def test_mapping_validate_document_boundaries():
    """R651: every validate_document limit is a CONTRACT boundary — exactly
    AT the limit passes, one past refuses (Gt→GtE and constant mutants all
    survived: no test sat on any edge)."""
    from app.integrations.services.mapping import (
        MAX_EXPR_LEN,
        MAX_TRANSFORMS,
        validate_document,
    )

    def doc(**field_extra):
        return {"fields": [{"target": "email", "path": "email", **field_extra}]}

    base = validate_document(doc())
    assert base == []

    # path length edge: == MAX_EXPR_LEN ok, +1 refused
    ok_path = "a" * MAX_EXPR_LEN
    assert validate_document(doc(path=ok_path)) == []
    probs = validate_document(doc(path=ok_path + "a"))
    assert any("path" in p for p in probs)

    # transforms count edge: == MAX_TRANSFORMS ok, +1 refused
    assert validate_document(doc(transform=["trim"] * MAX_TRANSFORMS)) == []
    probs = validate_document(doc(transform=["trim"] * (MAX_TRANSFORMS + 1)))
    assert any("more than" in p for p in probs)

    # enum_map: exactly 200 keys ok, 201 refused; non-dict refused; a non-str/
    # scalar VALUE refused (And→Or survived on the all() typecheck)
    em_ok = {f"k{i}": "v" for i in range(200)}
    assert validate_document(doc(enum_map=em_ok)) == []
    em_big = {f"k{i}": "v" for i in range(201)}
    assert any("enum_map" in p for p in validate_document(doc(enum_map=em_big)))
    assert any("enum_map" in p for p in validate_document(doc(enum_map=["not", "a", "dict"])))
    assert any("enum_map" in p for p in validate_document(doc(enum_map={"k": {"nested": 1}})))
    assert any("enum_map" in p for p in validate_document(doc(enum_map={1: "v"})))

    # document size cap: exactly 64KB passes, over refuses (pad via enum_map)
    pad = doc(enum_map={"k": ""})
    import json as _json

    base_len = len(_json.dumps(pad, default=str))
    pad["fields"][0]["enum_map"]["k"] = "x" * (65_536 - base_len)
    assert len(_json.dumps(pad, default=str)) == 65_536
    assert validate_document(pad) == []
    pad["fields"][0]["enum_map"]["k"] += "x"
    assert validate_document(pad) == ["document: exceeds 64KB"]


def test_mapping_to_int_refuses_bool_and_none():
    """R651 (Or→And survivor): booleans ARE ints in Python — without the
    explicit guard, active=true maps to 1 silently instead of failing the
    row. None likewise must be a transform error, not int('None')."""
    import pytest as _pytest

    from app.integrations.services.mapping import _t_to_int, _TransformError

    for bad in (True, False, None):
        with _pytest.raises(_TransformError):
            _t_to_int(bad)
    assert _t_to_int("42") == 42
    assert _t_to_int("") is None


def test_mapping_depth_and_string_len_edges():
    """R651: _depth counts levels exactly (Add→Sub / 1→2 survived) and
    apply_mapping's string cap sits at exactly MAX_STRING_LEN."""
    from app.integrations.services.mapping import (
        MAX_RESULT_DEPTH,
        MAX_STRING_LEN,
        _depth,
        apply_mapping,
    )

    assert _depth("leaf") == 0
    assert _depth({"a": "leaf"}) == 1
    assert _depth({"a": {"b": ["leaf"]}}) == 3
    # recursion guard: a structure deeper than the cap reports > cap but halts
    deep: dict = {"k": "v"}
    for _ in range(MAX_RESULT_DEPTH + 5):
        deep = {"k": deep}
    assert _depth(deep) > MAX_RESULT_DEPTH

    doc = {"fields": [{"target": "email", "path": "email"}]}
    ok, errors = apply_mapping(doc, {"email": "x" * MAX_STRING_LEN})
    assert errors == [] and len(ok["email"]) == MAX_STRING_LEN
    _, errors = apply_mapping(doc, {"email": "x" * (MAX_STRING_LEN + 1)})
    assert [e["code"] for e in errors] == ["too_long"]


def test_mapping_remaining_edges():
    """R651b: the rest of mapping.py's unpinned edges — int range ±2^53
    (exclusive both ends: beyond IEEE-754 exact-integer range a warehouse
    roundtrip silently corrupts), fields shape/count, target length,
    record input cap, default-application rule, and the depth gate's >=."""
    import json as _json

    import pytest as _pytest

    from app.integrations.services.mapping import (
        MAX_FIELDS,
        MAX_INPUT_BYTES,
        MAX_RESULT_DEPTH,
        _t_to_int,
        _TransformError,
        apply_mapping,
        validate_document,
    )

    # ±2^53 exclusive
    assert _t_to_int(2**53 - 1) == 2**53 - 1
    assert _t_to_int(-(2**53) + 1) == -(2**53) + 1
    for edge in (2**53, -(2**53), 2**53 + 7):
        with _pytest.raises(_TransformError):
            _t_to_int(edge)

    # fields: non-list AND empty-list each refuse on their own
    assert validate_document({"fields": {}}) == ["document.fields: required non-empty list"]
    assert validate_document({"fields": []}) == ["document.fields: required non-empty list"]

    # fields count: == MAX_FIELDS ok, +1 refused
    mk = lambda n: {"fields": [{"target": f"t{i}", "path": "p"} for i in range(n)]}  # noqa: E731
    assert validate_document(mk(MAX_FIELDS)) == []
    assert validate_document(mk(MAX_FIELDS + 1)) == [
        f"document.fields: more than {MAX_FIELDS} fields"
    ]

    # target: non-str / empty / 100 ok / 101 refused
    def tdoc(t):
        return {"fields": [{"target": t, "path": "p"}]}

    assert validate_document(tdoc("x" * 100)) == []
    for bad in (None, "", 7, "x" * 101):
        assert any(".target" in p for p in validate_document(tdoc(bad))), repr(bad)

    # record input cap: exactly MAX_INPUT_BYTES ok, +1 refused
    doc = {"fields": [{"target": "email", "path": "email"}]}
    rec = {"email": "a", "pad": ""}
    rec["pad"] = "x" * (MAX_INPUT_BYTES - len(_json.dumps(rec, default=str)))
    assert len(_json.dumps(rec, default=str)) == MAX_INPUT_BYTES
    _, errors = apply_mapping(doc, rec)
    assert errors == []
    rec["pad"] += "x"
    _, errors = apply_mapping(doc, rec)
    assert [e["code"] for e in errors] == ["input_too_large"]

    # default applies ONLY when the path yields None AND a default exists
    ddoc = {"fields": [{"target": "role", "path": "role", "default": "student"}]}
    out, errs = apply_mapping(ddoc, {})
    assert errs == [] and out["role"] == "student"
    out, _ = apply_mapping(ddoc, {"role": "admin"})
    assert out["role"] == "admin"  # present value never overwritten by default
    ndoc = {"fields": [{"target": "role", "path": "role"}]}
    out, errs = apply_mapping(ndoc, {})
    assert errs == [] and out.get("role") is None  # no default -> None passes through

    # transforms actually RUN through apply_mapping (`or []` -> `and []`
    # would silently skip every transform chain), and a None transform
    # list is tolerated
    tfdoc = {"fields": [{"target": "email", "path": "email", "transform": ["trim", "lower"]}]}
    out, errs = apply_mapping(tfdoc, {"email": "  MiXeD@Corp.EDU  "})
    assert errs == [] and out["email"] == "mixed@corp.edu"
    nonedoc = {"fields": [{"target": "email", "path": "email", "transform": None}]}
    out, errs = apply_mapping(nonedoc, {"email": "x@y.zz"})
    assert errs == [] and out["email"] == "x@y.zz"

    # depth gate is >=: depth == MAX_RESULT_DEPTH refused, one less accepted
    def nest(n):
        v = "leaf"
        for _ in range(n):
            v = {"k": v}
        return v

    vdoc = {"fields": [{"target": "blob", "path": "blob"}]}
    out, errs = apply_mapping(vdoc, {"blob": nest(MAX_RESULT_DEPTH - 1)})
    assert errs == [] and "blob" in out
    _, errs = apply_mapping(vdoc, {"blob": nest(MAX_RESULT_DEPTH)})
    assert [e["code"] for e in errs] == ["too_deep"]
