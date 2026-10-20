"""R609: property proofs for security-relevant pure helpers (DB-free).

The SSRF classifier gets a DUAL-IMPLEMENTATION check: the test declares the
forbidden address space as an explicit CIDR union (reading the RFCs, not the
code) and compares the production flag-based classifier against it across
randomly sampled 32-bit/128-bit address space — a flag-semantics surprise in
a future Python version fails here. The protocol parsers get hostile-input
totality (never raise, bounded output).
"""

import ipaddress

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
