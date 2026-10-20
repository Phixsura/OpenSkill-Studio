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
