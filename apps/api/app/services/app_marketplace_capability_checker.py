"""Capability Checker — verify sandbox supports required extension capabilities.

Checks that the sandbox environment provides all capabilities an
extension needs (filesystem, network, crypto, timers, etc.) before
allowing execution.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RESTRICTED = "restricted"
    DEPRECATED = "deprecated"


@dataclass
class Capability:
    name: str
    version: str
    status: CapabilityStatus
    description: str = ""
    restrictions: list[str] = field(default_factory=list)


# Platform-provided capabilities
PLATFORM_CAPABILITIES: dict[str, Capability] = {
    "filesystem": Capability("filesystem", "1.0", CapabilityStatus.AVAILABLE, "Virtual filesystem access"),
    "network.outbound": Capability("network.outbound", "1.0", CapabilityStatus.RESTRICTED, "Outbound HTTP", ["allowlist-only"]),
    "network.inbound": Capability("network.inbound", "1.0", CapabilityStatus.UNAVAILABLE, "Inbound connections"),
    "crypto": Capability("crypto", "1.0", CapabilityStatus.AVAILABLE, "Cryptographic operations"),
    "timers": Capability("timers", "1.0", CapabilityStatus.AVAILABLE, "setTimeout/setInterval"),
    "storage.kv": Capability("storage.kv", "1.0", CapabilityStatus.AVAILABLE, "Key-value storage"),
    "storage.blob": Capability("storage.blob", "1.0", CapabilityStatus.RESTRICTED, "Blob storage", ["max-10mb"]),
    "ipc": Capability("ipc", "1.0", CapabilityStatus.AVAILABLE, "Inter-process communication"),
    "events": Capability("events", "1.0", CapabilityStatus.AVAILABLE, "Event bus pub/sub"),
    "subprocess": Capability("subprocess", "1.0", CapabilityStatus.UNAVAILABLE, "Spawn child processes"),
    "native_modules": Capability("native_modules", "1.0", CapabilityStatus.UNAVAILABLE, "Native C/C++ modules"),
    "gpu": Capability("gpu", "0.1", CapabilityStatus.DEPRECATED, "GPU compute (use compute.v2)"),
}


class CapabilityChecker:
    """Checks sandbox capabilities against extension requirements."""

    def __init__(self, capabilities: dict[str, Capability] | None = None):
        self._capabilities = capabilities or dict(PLATFORM_CAPABILITIES)

    def check(self, required: list[str]) -> tuple[bool, list[dict]]:
        """Check if all required capabilities are available."""
        results = []
        all_ok = True
        for cap_name in required:
            cap = self._capabilities.get(cap_name)
            if not cap:
                results.append({"capability": cap_name, "status": "unknown", "ok": False,
                                "message": f"Unknown capability: {cap_name}"})
                all_ok = False
            elif cap.status == CapabilityStatus.AVAILABLE:
                results.append({"capability": cap_name, "status": "available", "ok": True})
            elif cap.status == CapabilityStatus.RESTRICTED:
                results.append({"capability": cap_name, "status": "restricted", "ok": True,
                                "restrictions": cap.restrictions})
            elif cap.status == CapabilityStatus.DEPRECATED:
                results.append({"capability": cap_name, "status": "deprecated", "ok": True,
                                "message": cap.description})
            else:
                results.append({"capability": cap_name, "status": "unavailable", "ok": False,
                                "message": f"{cap_name} is not available in sandbox"})
                all_ok = False
        return all_ok, results

    def list_available(self) -> list[str]:
        return sorted(n for n, c in self._capabilities.items()
                      if c.status in (CapabilityStatus.AVAILABLE, CapabilityStatus.RESTRICTED))

    def list_all(self) -> list[dict]:
        return [{"name": c.name, "version": c.version, "status": c.status.value,
                 "description": c.description} for c in self._capabilities.values()]

    def get_capability(self, name: str) -> Capability | None:
        return self._capabilities.get(name)

    def is_available(self, name: str) -> bool:
        cap = self._capabilities.get(name)
        return cap is not None and cap.status in (
            CapabilityStatus.AVAILABLE, CapabilityStatus.RESTRICTED)
