"""Service mesh sidecar manager — manage sidecar proxy configurations."""
from __future__ import annotations


class SidecarManager:
    def __init__(self):
        self._sidecars: dict[str, dict] = {}

    def inject(self, service: str, config: dict | None = None) -> dict:
        cfg = config or {"proxy": "envoy", "port": 15001, "mtls": True}
        self._sidecars[service] = {"service": service, "status": "injected", **cfg}
        return self._sidecars[service]

    def configure_mtls(self, service: str, enabled: bool) -> dict:
        if service in self._sidecars:
            self._sidecars[service]["mtls"] = enabled
        return {"service": service, "mtls": enabled}

    def traffic_policy(self, service: str, timeout_ms: int = 5000,
                       retries: int = 3, circuit_break: bool = True) -> dict:
        policy = {"timeout_ms": timeout_ms, "retries": retries, "circuit_break": circuit_break}
        if service in self._sidecars:
            self._sidecars[service]["policy"] = policy
        return {"service": service, "policy": policy}

    def stats(self) -> dict:
        mtls_count = sum(1 for s in self._sidecars.values() if s.get("mtls"))
        return {"total_sidecars": len(self._sidecars), "mtls_enabled": mtls_count}
