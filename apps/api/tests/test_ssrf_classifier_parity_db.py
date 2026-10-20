"""R589: cross-classifier SSRF parity guard.

The codebase carries THREE independent "is this IP forbidden for egress?"
implementations — fabric (app/integrations/security.py), the shared webhook
delivery guard (app/services/webhook.py), and ecosystem
(app/ecosystem/security.py). R587/R588 found the SAME fec0::/10 gap had to be
fixed in all three because they drifted independently.

Until they are consolidated into one shared validator, this test pins their
AGREEMENT: every address that ANY of them must block is blocked by ALL of
them, and every genuinely-public address is allowed by ALL of them. A future
one-copy fix (or a new copy) that drifts fails here.
"""

import ipaddress

import pytest

from app.ecosystem.security import _is_forbidden_ip as eco_forbidden
from app.integrations.security import _is_forbidden_ip as intg_forbidden
from app.services.webhook import _ip_blocked as webhook_blocked


def _webhook(ip_str: str) -> bool:
    # webhook's classifier takes an ipaddress object; an unparseable string
    # is rejected upstream in _is_blocked_url, so parity is only meaningful
    # for parseable addresses.
    return webhook_blocked(ipaddress.ip_address(ip_str))


CLASSIFIERS = {
    "integrations": intg_forbidden,
    "ecosystem": eco_forbidden,
    "webhook": _webhook,
}

MUST_BLOCK = [
    "10.1.2.3",
    "127.0.0.1",
    "169.254.169.254",  # cloud metadata
    "224.0.0.1",  # multicast
    "0.0.0.0",
    "::1",
    "::",
    "fe80::1",  # link-local
    "fc00::1",  # ULA
    "fec0::1",  # R587/R588: deprecated site-local
    "::ffff:10.0.0.1",  # IPv4-mapped private
    "::ffff:127.0.0.1",  # IPv4-mapped loopback
]

MUST_ALLOW = [
    "8.8.8.8",
    "1.1.1.1",
    "2607:f8b0::1",
    "::ffff:8.8.8.8",
]


@pytest.mark.parametrize("ip_str", MUST_BLOCK)
def test_all_classifiers_block(ip_str):
    offenders = [name for name, fn in CLASSIFIERS.items() if not fn(ip_str)]
    assert not offenders, f"{ip_str} ALLOWED by {offenders} (SSRF classifier drift)"


@pytest.mark.parametrize("ip_str", MUST_ALLOW)
def test_all_classifiers_allow_public(ip_str):
    blockers = [name for name, fn in CLASSIFIERS.items() if fn(ip_str)]
    assert not blockers, f"{ip_str} BLOCKED by {blockers} (over-blocks real public traffic)"


# ── URL-level scheme/userinfo rejection (fabric + ecosystem validators) ──
# These two expose a full URL validator that must reject non-http(s) schemes
# and embedded credentials. (The shared webhook service validates scheme at
# send time and IPs at create time; its URL-level parity is tracked in ADR
# R589 as a separate hardening item for the #27/#35 epics.)

import pytest as _pytest

from app.ecosystem.security import EcoSecurityError, validate_external_url
from app.integrations.security import EgressBlockedError, validate_egress_url

_URL_VALIDATORS = {
    "integrations": (validate_egress_url, EgressBlockedError),
    "ecosystem": (lambda u: validate_external_url(u, resolve_dns=False), EcoSecurityError),
}

_BAD_URLS = [
    "file:///etc/passwd",
    "gopher://evil/x",
    "ftp://host/x",
    "javascript:alert(1)",
    "https://user:pass@example.com/hook",  # embedded userinfo
]


@_pytest.mark.parametrize("name,pair", list(_URL_VALIDATORS.items()))
@_pytest.mark.parametrize("url", _BAD_URLS)
def test_url_validators_reject_bad_schemes_and_userinfo(name, pair, url):
    fn, exc = pair
    with _pytest.raises(exc):
        fn(url)
