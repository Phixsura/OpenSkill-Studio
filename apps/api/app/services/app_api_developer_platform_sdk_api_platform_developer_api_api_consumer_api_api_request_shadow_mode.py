"""API Consumer Request Shadow Mode — shadow test new API versions without affecting consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ShadowConfig:
    endpoint: str
    method: str
    shadow_version: str
    compare_responses: bool = True
    active: bool = True

@dataclass
class ShadowResult:
    request_id: str
    endpoint: str
    primary_status: int
    shadow_status: int
    match: bool
    diff_fields: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], ShadowConfig] = {}
        self._results: dict[str, list[ShadowResult]] = {}

    def configure(self, installation_id: str, config: ShadowConfig) -> ShadowConfig:
        if not installation_id: raise ValueError("installation_id is required")
        self._configs[(installation_id, config.method.upper(), config.endpoint)] = config
        return config

    def is_shadowed(self, installation_id: str, method: str, endpoint: str) -> bool:
        config = self._configs.get((installation_id, method.upper(), endpoint))
        return config is not None and config.active

    def record_result(self, installation_id: str, result: ShadowResult) -> ShadowResult:
        self._results.setdefault(installation_id, []).append(result)
        return result

    def match_rate(self, installation_id: str) -> float:
        results = self._results.get(installation_id, [])
        if not results: return 0.0
        return round(sum(1 for r in results if r.match) / len(results) * 100, 1)

    def mismatches(self, installation_id: str, limit: int = 20) -> list[ShadowResult]:
        return [r for r in self._results.get(installation_id, []) if not r.match][-limit:]

    def list_configs(self, installation_id: str) -> list[ShadowConfig]:
        return [c for (inst, _, _), c in self._configs.items() if inst == installation_id]
