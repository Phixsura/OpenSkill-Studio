"""Security guards for external content (ADR-016 Part Q).

All external text/files are untrusted data: no tool invocation, no code
execution, strict schema extraction, bounded sizes, SSRF-safe fetching,
archive/path-traversal protection.
"""

import ipaddress
import json
import re
import socket
from urllib.parse import urlparse

from app.exceptions import AppError

# Ports allowed for external sources (standard web + common alt TLS)
ALLOWED_PORTS = frozenset({80, 443, 8443})

# Hard caps for bounded parsing (ADR-016 §4.1)
MAX_JSON_BYTES = 5_242_880
MAX_JSON_DEPTH = 20
MAX_JSON_STRING = 100_000
MAX_JSON_KEYS = 10_000

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# TLDs that always indicate internal infrastructure
_BLOCKED_TLDS = (".internal", ".local", ".localhost", ".corp", ".home", ".lan")


class EcoSecurityError(AppError):
    """Security violation while handling external content."""

    def __init__(self, code: str, message: str, status_code: int = 422):
        super().__init__(code=code, message=message, status_code=status_code)


def _is_forbidden_ip(ip_str: str) -> bool:
    """True if the address is private/reserved/loopback/link-local/metadata."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # unparseable — refuse
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validate_external_url(url: str, *, resolve_dns: bool = True) -> str:
    """SSRF guard: validate an external URL before any fetch.

    Rejects non-http(s) schemes, userinfo, non-standard ports, internal TLDs,
    literal private/reserved IPs, and (when resolve_dns) hostnames resolving
    to private ranges. Returns the normalized URL.
    """
    if not url or len(url) > 2000:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "URL missing or too long")
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "URL could not be parsed") from exc
    if parsed.scheme not in ("http", "https"):
        raise EcoSecurityError("ECO_SSRF_BLOCKED", f"Scheme not allowed: {parsed.scheme!r}")
    if parsed.username or parsed.password:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "Userinfo in URL not allowed")
    host = parsed.hostname
    if not host:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "URL has no hostname")
    port = parsed.port
    if port is not None and port not in ALLOWED_PORTS:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", f"Port not allowed: {port}")
    lowered = host.lower().rstrip(".")
    if lowered == "localhost" or lowered.endswith(_BLOCKED_TLDS):
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "Internal hostname not allowed")
    # Literal IP?
    try:
        ipaddress.ip_address(lowered)
        is_literal_ip = True
    except ValueError:
        is_literal_ip = False
    if is_literal_ip:
        if _is_forbidden_ip(lowered):
            raise EcoSecurityError("ECO_SSRF_BLOCKED", "IP address in private/reserved range")
        return url
    # Hostname without a dot is never a public host
    if "." not in lowered:
        raise EcoSecurityError("ECO_SSRF_BLOCKED", "Hostname is not a public FQDN")
    if resolve_dns:
        try:
            infos = socket.getaddrinfo(lowered, port or 443, proto=socket.IPPROTO_TCP)
        except OSError as exc:
            raise EcoSecurityError("ECO_SSRF_BLOCKED", "Hostname did not resolve") from exc
        for info in infos:
            addr = info[4][0]
            if _is_forbidden_ip(addr):
                raise EcoSecurityError(
                    "ECO_SSRF_BLOCKED", "Hostname resolves to a private/reserved address"
                )
    return url


def _check_bounds(value, depth: int, counter: dict) -> None:
    if depth > MAX_JSON_DEPTH:
        raise EcoSecurityError("ECO_PAYLOAD_TOO_DEEP", f"JSON nesting exceeds {MAX_JSON_DEPTH}")
    if isinstance(value, dict):
        counter["keys"] += len(value)
        if counter["keys"] > MAX_JSON_KEYS:
            raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", "Too many JSON keys", 413)
        for k, v in value.items():
            if isinstance(k, str) and len(k) > MAX_JSON_STRING:
                raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", "JSON key too long", 413)
            _check_bounds(v, depth + 1, counter)
    elif isinstance(value, list):
        counter["keys"] += len(value)
        if counter["keys"] > MAX_JSON_KEYS:
            raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", "Too many JSON items", 413)
        for v in value:
            _check_bounds(v, depth + 1, counter)
    elif isinstance(value, str):
        if len(value) > MAX_JSON_STRING:
            raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", "JSON string too long", 413)
    elif isinstance(value, float):
        # NaN/Infinity cannot be stored in JSONB and 500 downstream (R87)
        if value != value or value in (float("inf"), float("-inf")):
            raise EcoSecurityError("ECO_PAYLOAD_TOO_DEEP", "Non-finite number in payload")


def bounded_json_loads(raw: bytes | str, *, max_bytes: int = MAX_JSON_BYTES):
    """Parse untrusted JSON with size/depth/width/string bounds enforced."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8", errors="replace")
    if len(raw) > max_bytes:
        raise EcoSecurityError("ECO_PAYLOAD_TOO_LARGE", f"Payload exceeds {max_bytes} bytes", 413)
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise EcoSecurityError("ECO_PAYLOAD_MALFORMED", f"Invalid JSON: {exc}") from exc
    _check_bounds(parsed, 0, {"keys": 0})
    return parsed


def sanitize_text(value, max_len: int = 2000) -> str | None:
    """Strip NUL/control chars from untrusted text and bound its length.

    Postgres TEXT/JSONB rejects NUL bytes with a 500 unless screened (R87).
    Non-string inputs return None (strict extraction: never coerce).
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    cleaned = _CONTROL_CHARS_RE.sub("", value)
    return cleaned[:max_len]


def safe_archive_member(name: str) -> bool:
    """True if an archive member name is traversal-safe (relative, no ..)."""
    if not name or name.startswith(("/", "\\")):
        return False
    if re.match(r"^[a-zA-Z]:", name):  # Windows drive
        return False
    parts = name.replace("\\", "/").split("/")
    return ".." not in parts


# Patterns that indicate prompt-injection attempts in fetched text. Matched
# content is still stored (append-only ledger) but flagged and never passed
# to any LLM extraction without the fixed instruction frame.
_INJECTION_PATTERNS = re.compile(
    r"(ignore (all |any )?(previous|prior|above) instructions"
    r"|disregard (the |your )?system prompt"
    r"|you are now"
    r"|<\s*/?(system|assistant|tool_call|function_call)\b"
    r"|\bBEGIN (SYSTEM|ADMIN) (PROMPT|MESSAGE)\b)",
    re.IGNORECASE,
)


def looks_like_prompt_injection(text: str) -> bool:
    """Heuristic flag for injection-shaped external text (Part Q)."""
    if not isinstance(text, str):
        return False
    return bool(_INJECTION_PATTERNS.search(text))


def escape_like(value: str) -> str:
    """Escape LIKE/ILIKE wildcards in user-supplied search text so a query
    for "50%_off" matches literally instead of turning into a wildcard scan.
    Use with .ilike(..., escape="\\")."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
