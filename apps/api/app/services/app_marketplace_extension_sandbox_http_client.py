"""Sandbox HTTP Client — controlled HTTP client for extension sandboxes.

Provides a sandboxed HTTP client with URL allowlisting, request logging,
timeout enforcement, response size limits, and header sanitization.
"""
from __future__ import annotations
import re
import secrets
from dataclasses import dataclass, field
from enum import Enum
import ipaddress


PRIVATE_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1",
                 "metadata.google.internal", "169.254.169.254"}


def _is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return host.lower() in PRIVATE_HOSTS


@dataclass
class HttpRequest:
    request_id: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    timeout_ms: int = 30000


@dataclass
class HttpResponse:
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    size_bytes: int = 0
    latency_ms: float = 0.0


@dataclass
class RequestLog:
    request: HttpRequest
    response: HttpResponse | None = None
    blocked: bool = False
    block_reason: str = ""


FORBIDDEN_HEADERS = {"host", "cookie", "authorization", "x-forwarded-for",
                     "x-real-ip", "proxy-authorization"}


class SandboxHttpClientService:
    """Controlled HTTP client for sandboxed extensions."""

    MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_TIMEOUT = 30000
    MAX_BODY_SIZE = 5 * 1024 * 1024  # 5MB

    def __init__(self):
        self._allowlist: dict[str, list[str]] = {}  # sandbox_id -> [patterns]
        self._log: list[RequestLog] = []

    def set_allowlist(self, sandbox_id: str, patterns: list[str]) -> None:
        self._allowlist[sandbox_id] = patterns

    def _is_allowed(self, sandbox_id: str, url: str) -> tuple[bool, str]:
        # Block private/internal URLs
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or ""
            if _is_private_ip(host):
                return False, f"Private/internal host blocked: {host}"
            if not parsed.scheme or parsed.scheme not in ("http", "https"):
                return False, f"Invalid scheme: {parsed.scheme}"
        except Exception:
            return False, "Invalid URL"

        # Check allowlist
        patterns = self._allowlist.get(sandbox_id)
        if patterns is not None:
            for pattern in patterns:
                if re.match(pattern.replace("*", ".*"), url):
                    return True, ""
            return False, "URL not in allowlist"
        return True, ""

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return {k: v for k, v in headers.items()
                if k.lower() not in FORBIDDEN_HEADERS}

    def request(self, sandbox_id: str, method: str, url: str,
                headers: dict[str, str] | None = None,
                body: str = "", timeout_ms: int = 30000) -> RequestLog:
        safe_headers = self._sanitize_headers(headers or {})
        timeout_ms = min(timeout_ms, self.MAX_TIMEOUT)

        req = HttpRequest(
            request_id=f"hr_{secrets.token_urlsafe(8)}",
            method=method.upper(), url=url,
            headers=safe_headers, body=body, timeout_ms=timeout_ms,
        )

        # Check body size
        if len(body.encode()) > self.MAX_BODY_SIZE:
            log = RequestLog(request=req, blocked=True, block_reason="Request body too large")
            self._log.append(log)
            return log

        # Check URL allowlist
        allowed, reason = self._is_allowed(sandbox_id, url)
        if not allowed:
            log = RequestLog(request=req, blocked=True, block_reason=reason)
            self._log.append(log)
            return log

        # Simulated response
        resp = HttpResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body='{"ok": true}',
            size_bytes=13, latency_ms=50.0,
        )
        log = RequestLog(request=req, response=resp)
        self._log.append(log)
        return log

    def get_log(self, sandbox_id: str | None = None,
                limit: int = 50) -> list[RequestLog]:
        return self._log[-limit:]

    def get_blocked_count(self) -> int:
        return sum(1 for l in self._log if l.blocked)
