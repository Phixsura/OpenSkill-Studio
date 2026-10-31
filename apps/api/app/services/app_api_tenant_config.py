"""App API Tenant Config — per-tenant configuration overrides.

Manages tenant configs:
- Store key-value overrides per tenant
- Merge with defaults
- Track config changes
- Per-installation scoped configs
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


class AppAPITenantConfig:
    """Per-tenant configuration overrides."""

    def __init__(self) -> None:
        self._defaults: dict[str, dict[str, str]] = {}
        self._overrides: dict[tuple[str, str], dict[str, str]] = {}

    def set_defaults(self, installation_id: str, config: dict[str, str]) -> dict[str, str]:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._defaults[installation_id] = dict(config)
        return self._defaults[installation_id]

    def set_override(
        self, installation_id: str, tenant_id: str, key: str, value: str,
    ) -> dict[str, str]:
        k = (installation_id, tenant_id)
        overrides = self._overrides.setdefault(k, {})
        overrides[key] = value
        return overrides

    def get_config(self, installation_id: str, tenant_id: str) -> dict[str, str]:
        """Get merged config: defaults + tenant overrides."""
        defaults = dict(self._defaults.get(installation_id, {}))
        overrides = self._overrides.get((installation_id, tenant_id), {})
        defaults.update(overrides)
        return defaults

    def get_override_keys(self, installation_id: str, tenant_id: str) -> list[str]:
        return sorted(self._overrides.get((installation_id, tenant_id), {}).keys())

    def remove_override(self, installation_id: str, tenant_id: str, key: str) -> bool:
        overrides = self._overrides.get((installation_id, tenant_id), {})
        if key in overrides:
            del overrides[key]
            return True
        return False
