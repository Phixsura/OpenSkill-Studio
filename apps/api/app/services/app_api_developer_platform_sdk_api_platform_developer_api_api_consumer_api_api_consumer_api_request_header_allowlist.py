"""API Consumer Request Header Allowlist — restrict which headers consumers can send."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HeaderAllowlist:
    consumer_id: str
    allowed_headers: set[str] = field(default_factory=set)
    strip_unknown: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestHeaderAllowlist:
    def __init__(self) -> None:
        self._lists: dict[tuple[str, str], HeaderAllowlist] = {}
        # Standard always-allowed
        self._default_allowed = {"content-type", "accept", "accept-encoding", "user-agent", "authorization"}

    def set_allowlist(self, installation_id: str, config: HeaderAllowlist) -> HeaderAllowlist:
        if not installation_id: raise ValueError("installation_id is required")
        config.allowed_headers = {h.lower() for h in config.allowed_headers}
        self._lists[(installation_id, config.consumer_id)] = config
        return config

    def filter_headers(self, installation_id: str, consumer_id: str, headers: dict[str, str]) -> dict[str, str]:
        config = self._lists.get((installation_id, consumer_id))
        if config is None: return dict(headers)
        allowed = config.allowed_headers | self._default_allowed
        if not config.strip_unknown: return dict(headers)
        return {k: v for k, v in headers.items() if k.lower() in allowed}

    def is_allowed(self, installation_id: str, consumer_id: str, header_name: str) -> bool:
        config = self._lists.get((installation_id, consumer_id))
        if config is None: return True
        return header_name.lower() in (config.allowed_headers | self._default_allowed)

    def list_allowlists(self, installation_id: str) -> list[HeaderAllowlist]:
        return [a for (inst, _), a in self._lists.items() if inst == installation_id]
