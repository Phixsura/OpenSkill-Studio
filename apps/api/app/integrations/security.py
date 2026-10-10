"""Integration fabric security — the single egress path (ADR-018 §14.1).

Every outbound byte from app/integrations/ (webhook delivery, connector
calls, IdP metadata fetch) goes through EgressClient. Direct httpx use
anywhere else in the package is forbidden (a lint test asserts it).

Design (research S8.1):
- Validate the RESOLVED IPs, not the URL string — every private/reserved
  range, IPv4-mapped IPv6, and numeric-encoding form is rejected.
- Pin the connection: resolve once, validate, then dial that exact IP with
  the Host header + SNI set to the original hostname. No re-resolution
  between validation and connect ⇒ no DNS-rebinding window.
- Re-validate on EVERY dispatch (registration-time checks don't survive a
  TTL flip before a retry hours later).
- Schemes http/https only; redirects are terminal responses (never
  followed); response size and timeouts capped.
- APP_ENV=test may allow private ranges (settings.egress_allow_private)
  because E2E suites target localhost (R79 pattern). The config module
  refuses the flag outside test.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

import httpx

from app.config import settings
from app.exceptions import AppError

MAX_URL_LEN = 500
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB
CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 15.0

_ALLOWED_PORTS = frozenset({80, 443, 8080, 8443})
_BLOCKED_TLDS = (".internal", ".local", ".localhost", ".corp", ".home", ".lan")


class EgressBlockedError(AppError):
    """Outbound request refused by the SSRF guard (always a 422 — the URL is
    client-controlled input, not a server fault)."""

    def __init__(self, message: str):
        super().__init__("EGRESS_BLOCKED", message, 422)


def _is_forbidden_ip(ip_str: str) -> bool:
    """True when the address must never be dialed (private/reserved/meta)."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    # Unwrap IPv4-mapped IPv6 (::ffff:10.0.0.1) before classification.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        # Carrier-grade NAT (100.64/10) — not covered by is_private.
        or (isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network("100.64.0.0/10"))
    )


def _resolve_and_validate(host: str, port: int) -> str:
    """Resolve ``host`` and validate EVERY returned address; return the first.

    Raising on any forbidden address (rather than skipping to a public one)
    is deliberate: a hostname that resolves to a mixed public+private set is
    an attack, not a CDN.
    """
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except OSError as exc:
        raise EgressBlockedError("Hostname did not resolve") from exc
    addrs = [info[4][0] for info in infos]
    if not addrs:
        raise EgressBlockedError("Hostname did not resolve")
    if not settings.egress_allow_private:
        for addr in addrs:
            if _is_forbidden_ip(addr):
                raise EgressBlockedError("Hostname resolves to a private/reserved address")
    return addrs[0]


def validate_egress_url(url: str) -> str:
    """Parse+screen an outbound URL (scheme/host/port/userinfo); returns the
    normalized URL. DNS resolution happens at request time (per dispatch)."""
    if not url or len(url) > MAX_URL_LEN:
        raise EgressBlockedError("URL missing or too long")
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise EgressBlockedError("URL could not be parsed") from exc
    if parsed.scheme not in ("http", "https"):
        raise EgressBlockedError(f"Scheme not allowed: {parsed.scheme!r}")
    if parsed.scheme == "http" and not settings.egress_allow_private:
        raise EgressBlockedError("Plain http egress is not allowed")
    if "@" in parsed.netloc:
        raise EgressBlockedError("Userinfo in URL not allowed")
    host = parsed.hostname
    if not host:
        raise EgressBlockedError("URL has no hostname")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in _ALLOWED_PORTS:
        raise EgressBlockedError(f"Port not allowed: {port}")
    lowered = host.lower().rstrip(".")
    if (lowered.endswith(_BLOCKED_TLDS) or lowered == "localhost") and (
        not settings.egress_allow_private
    ):
        raise EgressBlockedError("Internal hostname not allowed")
    # Literal IPs are screened immediately (no DNS step to defer to).
    try:
        ipaddress.ip_address(lowered.strip("[]"))
    except ValueError:
        pass
    else:
        if not settings.egress_allow_private and _is_forbidden_ip(lowered.strip("[]")):
            raise EgressBlockedError("IP address in private/reserved range")
    return url


class EgressClient:
    """SSRF-safe outbound HTTP. One instance per call site; stateless."""

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        read_timeout: float = READ_TIMEOUT,
    ) -> httpx.Response:
        validate_egress_url(url)
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        # Resolve + validate NOW, then dial the literal IP with Host/SNI set
        # to the hostname — the client never re-resolves (rebinding defense).
        pinned_ip = _resolve_and_validate(host, port)
        ip_literal = f"[{pinned_ip}]" if ":" in pinned_ip else pinned_ip
        pinned_url = f"{parsed.scheme}://{ip_literal}:{port}{parsed.path or '/'}"
        if parsed.query:
            pinned_url += f"?{parsed.query}"

        send_headers = dict(headers or {})
        send_headers["Host"] = host if port in (80, 443) else f"{host}:{port}"
        extensions = {}
        if parsed.scheme == "https":
            # httpcore uses sni_hostname for both SNI and cert verification,
            # so TLS still authenticates the real hostname, not the IP.
            extensions["sni_hostname"] = host

        timeout = httpx.Timeout(connect=CONNECT_TIMEOUT, read=read_timeout, write=10.0, pool=5.0)
        async with httpx.AsyncClient(
            follow_redirects=False, timeout=timeout, trust_env=False
        ) as client:
            resp = await client.request(
                method,
                pinned_url,
                headers=send_headers,
                content=content,
                extensions=extensions,
            )
            # Cap what we hold in memory; callers never stream.
            if len(resp.content) > MAX_RESPONSE_BYTES:
                raise EgressBlockedError("Response exceeds size cap")
            return resp
