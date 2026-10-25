"""Install Manager — manage extension installation lifecycle per organization.

Handles install, uninstall, enable, disable, and upgrade of extensions
per org with dependency resolution and rollback support.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class InstallState(str, Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UPGRADING = "upgrading"
    FAILED = "failed"


@dataclass
class Installation:
    extension_id: str
    org_id: str
    version: str
    state: InstallState
    installed_at: str
    installed_by: str
    config: dict = field(default_factory=dict)
    previous_version: str = ""


class InstallManager:
    """Manages extension installations per organization."""

    def __init__(self):
        self._installs: dict[str, dict[str, Installation]] = {}  # org -> ext -> install

    def install(self, org_id: str, extension_id: str, version: str,
                installed_by: str, config: dict | None = None) -> tuple[Installation | None, str]:
        """Install an extension for an organization."""
        org_installs = self._installs.setdefault(org_id, {})
        if extension_id in org_installs:
            return None, "Extension already installed"
        now = datetime.now(timezone.utc).isoformat()
        inst = Installation(
            extension_id=extension_id, org_id=org_id, version=version,
            state=InstallState.ENABLED, installed_at=now,
            installed_by=installed_by, config=config or {},
        )
        org_installs[extension_id] = inst
        return inst, "Installed successfully"

    def uninstall(self, org_id: str, extension_id: str) -> bool:
        org_installs = self._installs.get(org_id, {})
        return org_installs.pop(extension_id, None) is not None

    def enable(self, org_id: str, extension_id: str) -> bool:
        inst = self._get(org_id, extension_id)
        if inst and inst.state == InstallState.DISABLED:
            inst.state = InstallState.ENABLED
            return True
        return False

    def disable(self, org_id: str, extension_id: str) -> bool:
        inst = self._get(org_id, extension_id)
        if inst and inst.state == InstallState.ENABLED:
            inst.state = InstallState.DISABLED
            return True
        return False

    def upgrade(self, org_id: str, extension_id: str, new_version: str) -> tuple[bool, str]:
        inst = self._get(org_id, extension_id)
        if not inst:
            return False, "Not installed"
        if inst.version == new_version:
            return False, "Already on this version"
        inst.previous_version = inst.version
        inst.version = new_version
        inst.state = InstallState.ENABLED
        return True, f"Upgraded {inst.previous_version} -> {new_version}"

    def rollback(self, org_id: str, extension_id: str) -> tuple[bool, str]:
        inst = self._get(org_id, extension_id)
        if not inst or not inst.previous_version:
            return False, "No previous version to rollback to"
        old = inst.version
        inst.version = inst.previous_version
        inst.previous_version = ""
        inst.state = InstallState.ENABLED
        return True, f"Rolled back {old} -> {inst.version}"

    def get_installation(self, org_id: str, extension_id: str) -> Installation | None:
        return self._get(org_id, extension_id)

    def list_installed(self, org_id: str, state: InstallState | None = None) -> list[Installation]:
        installs = list(self._installs.get(org_id, {}).values())
        if state:
            installs = [i for i in installs if i.state == state]
        return installs

    def _get(self, org_id: str, ext_id: str) -> Installation | None:
        return self._installs.get(org_id, {}).get(ext_id)
