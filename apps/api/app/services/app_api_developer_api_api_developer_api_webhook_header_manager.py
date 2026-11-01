"""App API Developer Webhook Header Manager — manage custom headers per destination."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_FORBIDDEN_HEADERS = {"host", "content-length", "transfer-encoding"}
_HEADER_NAME_RE = re.compile(r"^[A-Za-z0-9\-]+$")

@dataclass
class HeaderConfig:
    destination: str
    headers: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperAPIApiDeveloperApiWebhookHeaderManager:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], HeaderConfig] = {}

    def set_headers(self, installation_id: str, destination: str, headers: dict[str, str]) -> HeaderConfig:
        if not installation_id: raise ValueError("installation_id is required")
        for name in headers:
            if not _HEADER_NAME_RE.match(name): raise ValueError(f"Invalid header name: {name}")
            if name.lower() in _FORBIDDEN_HEADERS: raise ValueError(f"Forbidden header: {name}")
        key = (installation_id, destination)
        c = HeaderConfig(destination=destination, headers=dict(headers))
        self._configs[key] = c
        return c

    def add_header(self, installation_id: str, destination: str, name: str, value: str) -> HeaderConfig:
        if not _HEADER_NAME_RE.match(name): raise ValueError(f"Invalid header name: {name}")
        if name.lower() in _FORBIDDEN_HEADERS: raise ValueError(f"Forbidden header: {name}")
        key = (installation_id, destination)
        c = self._configs.setdefault(key, HeaderConfig(destination=destination))
        c.headers[name] = value
        return c

    def remove_header(self, installation_id: str, destination: str, name: str) -> HeaderConfig:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No config for {destination}")
        c.headers.pop(name, None)
        return c

    def get_headers(self, installation_id: str, destination: str) -> dict[str, str]:
        key = (installation_id, destination)
        c = self._configs.get(key)
        return dict(c.headers) if c else {}

    def all_configs(self, installation_id: str) -> list[HeaderConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
