"""Compatibility Checker — verify extension compatibility with platform versions.

Checks that extensions declare minimum/maximum platform version support,
validates runtime compatibility, and detects breaking changes.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CompatibilitySpec:
    extension_id: str
    min_platform_version: str
    max_platform_version: str = ""  # empty = no upper bound
    required_apis: list[str] = field(default_factory=list)
    incompatible_extensions: list[str] = field(default_factory=list)


def _parse_ver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


class CompatibilityChecker:
    """Checks extension compatibility with platform and other extensions."""

    def __init__(self, platform_version: str = "1.0.0",
                 available_apis: list[str] | None = None):
        self._platform_ver = platform_version
        self._available_apis = set(available_apis if available_apis is not None else [
            "extensions.v1", "webhooks.v1", "config.v1", "events.v1",
            "analytics.v1", "sandbox.v1", "auth.v1", "storage.v1",
        ])
        self._specs: dict[str, CompatibilitySpec] = {}

    def register_spec(self, spec: CompatibilitySpec) -> None:
        self._specs[spec.extension_id] = spec

    def check_platform_version(self, extension_id: str) -> tuple[bool, str]:
        """Check if extension is compatible with current platform version."""
        spec = self._specs.get(extension_id)
        if not spec:
            return True, "No compatibility spec registered"
        current = _parse_ver(self._platform_ver)
        min_ver = _parse_ver(spec.min_platform_version)
        if current < min_ver:
            return False, f"Requires platform >= {spec.min_platform_version}, current is {self._platform_ver}"
        if spec.max_platform_version:
            max_ver = _parse_ver(spec.max_platform_version)
            if current > max_ver:
                return False, f"Requires platform <= {spec.max_platform_version}, current is {self._platform_ver}"
        return True, "Compatible"

    def check_apis(self, extension_id: str) -> tuple[bool, list[str]]:
        """Check if all required APIs are available."""
        spec = self._specs.get(extension_id)
        if not spec:
            return True, []
        missing = [api for api in spec.required_apis if api not in self._available_apis]
        return len(missing) == 0, missing

    def check_conflicts(self, extension_id: str, installed: list[str]) -> list[str]:
        """Check for conflicts with installed extensions."""
        spec = self._specs.get(extension_id)
        if not spec:
            return []
        return [ext for ext in spec.incompatible_extensions if ext in installed]

    def full_check(self, extension_id: str, installed: list[str] | None = None) -> dict:
        """Run all compatibility checks."""
        ver_ok, ver_msg = self.check_platform_version(extension_id)
        api_ok, missing_apis = self.check_apis(extension_id)
        conflicts = self.check_conflicts(extension_id, installed or [])
        compatible = ver_ok and api_ok and len(conflicts) == 0
        return {
            "extension_id": extension_id,
            "compatible": compatible,
            "platform_version": {"ok": ver_ok, "message": ver_msg},
            "apis": {"ok": api_ok, "missing": missing_apis},
            "conflicts": conflicts,
        }
