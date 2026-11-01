"""App Capability Registry — declare and query app capabilities.

Manages capability declarations for installed apps:
- Declare capabilities with versions
- Query apps by capability
- Capability negotiation (min version checks)
- Per-installation scoped capabilities
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Capability:
    """A declared capability."""

    capability_id: str
    name: str
    version: str
    description: str = ""


class AppCapabilityRegistry:
    """Declare and query app capabilities."""

    def __init__(self) -> None:
        # (installation_id, capability_id) → Capability
        self._caps: dict[tuple[str, str], Capability] = {}

    def declare(
        self,
        installation_id: str,
        capability_id: str,
        name: str,
        version: str,
        description: str = "",
    ) -> Capability:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not capability_id:
            raise ValueError("capability_id is required")
        if not version:
            raise ValueError("version is required")

        cap = Capability(
            capability_id=capability_id, name=name,
            version=version, description=description,
        )
        self._caps[(installation_id, capability_id)] = cap
        return cap

    def has_capability(
        self, installation_id: str, capability_id: str
    ) -> bool:
        return (installation_id, capability_id) in self._caps

    def get_capability(
        self, installation_id: str, capability_id: str
    ) -> Capability:
        key = (installation_id, capability_id)
        cap = self._caps.get(key)
        if cap is None:
            raise KeyError(f"Capability {capability_id} not found")
        return cap

    def check_version(
        self,
        installation_id: str,
        capability_id: str,
        min_version: str,
    ) -> bool:
        """Check if a capability meets minimum version."""
        key = (installation_id, capability_id)
        cap = self._caps.get(key)
        if cap is None:
            return False
        return self._compare_versions(cap.version, min_version) >= 0

    def list_capabilities(self, installation_id: str) -> list[Capability]:
        return [c for (inst, _), c in self._caps.items() if inst == installation_id]

    def find_installations_with(self, capability_id: str) -> list[str]:
        """Find all installations that have a capability."""
        return sorted({
            inst for (inst, cid) in self._caps if cid == capability_id
        })

    def revoke(self, installation_id: str, capability_id: str) -> bool:
        key = (installation_id, capability_id)
        if key in self._caps:
            del self._caps[key]
            return True
        return False

    def _compare_versions(self, a: str, b: str) -> int:
        """Compare version strings. Returns -1, 0, or 1."""
        pa = [int(x) for x in a.split(".") if x.isdigit()]
        pb = [int(x) for x in b.split(".") if x.isdigit()]
        for x, y in zip(pa, pb):
            if x < y:
                return -1
            if x > y:
                return 1
        return len(pa) - len(pb)
