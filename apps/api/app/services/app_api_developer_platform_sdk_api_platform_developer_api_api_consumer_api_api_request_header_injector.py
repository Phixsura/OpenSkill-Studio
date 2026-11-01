"""API Consumer Request Header Injector — inject custom headers into API requests."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_HEADER_NAME_RE = re.compile(r"^[A-Za-z0-9\-]+$")
_HEADER_VALUE_RE = re.compile(r"^[\x20-\x7E\t]*$")
_FORBIDDEN = {"host", "content-length", "transfer-encoding", "connection"}

@dataclass
class HeaderInjectionRule:
    rule_id: str
    header_name: str
    header_value: str
    override: bool = False  # if True, overwrite existing

@dataclass
class InjectionConfig:
    consumer_id: str
    rules: list[HeaderInjectionRule] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], InjectionConfig] = {}

    def configure(self, installation_id: str, config: InjectionConfig) -> InjectionConfig:
        if not installation_id: raise ValueError("installation_id is required")
        for r in config.rules:
            if not _HEADER_NAME_RE.match(r.header_name): raise ValueError(f"Invalid header name: {r.header_name}")
            if not _HEADER_VALUE_RE.match(r.header_value): raise ValueError("Header value contains control characters")
            if r.header_name.lower() in _FORBIDDEN: raise ValueError(f"Cannot inject forbidden header: {r.header_name}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def inject(self, installation_id: str, consumer_id: str, headers: dict[str, str]) -> dict[str, str]:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return dict(headers)
        result = dict(headers)
        for r in config.rules:
            if r.header_name in result and not r.override: continue
            result[r.header_name] = r.header_value
        return result

    def list_configs(self, installation_id: str) -> list[InjectionConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
