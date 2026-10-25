"""Environment Manager — manage environment variables for sandboxed extensions.

Provides secure environment variable injection for extension sandboxes
with encryption markers, validation, and scope isolation per org.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EnvVar:
    key: str
    value: str
    encrypted: bool = False
    scope: str = "extension"  # "extension", "org", "global"
    description: str = ""


class EnvironmentManager:
    """Manages environment variables for extension sandboxes."""

    RESERVED_PREFIXES = ("OPENSKILL_", "SYSTEM_", "PATH", "HOME")
    MAX_KEY_LENGTH = 128
    MAX_VALUE_LENGTH = 8192
    MAX_VARS_PER_SCOPE = 100

    def __init__(self):
        self._vars: dict[str, dict[str, EnvVar]] = {}  # scope_key -> {key: EnvVar}

    def _scope_key(self, extension_id: str, org_id: str = "") -> str:
        return f"{extension_id}:{org_id}" if org_id else extension_id

    def _validate_key(self, key: str) -> tuple[bool, str]:
        if not key or not key.replace("_", "").isalnum():
            return False, "Key must be alphanumeric with underscores"
        if len(key) > self.MAX_KEY_LENGTH:
            return False, f"Key exceeds {self.MAX_KEY_LENGTH} characters"
        for prefix in self.RESERVED_PREFIXES:
            if key.upper().startswith(prefix):
                return False, f"Key prefix '{prefix}' is reserved"
        return True, ""

    def set_var(self, extension_id: str, key: str, value: str,
                org_id: str = "", encrypted: bool = False,
                description: str = "") -> tuple[bool, str]:
        """Set an environment variable."""
        valid, err = self._validate_key(key)
        if not valid:
            return False, err
        if len(value) > self.MAX_VALUE_LENGTH:
            return False, f"Value exceeds {self.MAX_VALUE_LENGTH} characters"

        sk = self._scope_key(extension_id, org_id)
        scope_vars = self._vars.setdefault(sk, {})
        if key not in scope_vars and len(scope_vars) >= self.MAX_VARS_PER_SCOPE:
            return False, "Maximum variables per scope reached"

        scope = "org" if org_id else "extension"
        scope_vars[key] = EnvVar(key=key, value=value, encrypted=encrypted,
                                  scope=scope, description=description)
        return True, "Set"

    def get_var(self, extension_id: str, key: str, org_id: str = "") -> EnvVar | None:
        sk = self._scope_key(extension_id, org_id)
        return self._vars.get(sk, {}).get(key)

    def delete_var(self, extension_id: str, key: str, org_id: str = "") -> bool:
        sk = self._scope_key(extension_id, org_id)
        return self._vars.get(sk, {}).pop(key, None) is not None

    def list_vars(self, extension_id: str, org_id: str = "",
                  mask_encrypted: bool = True) -> list[dict]:
        """List environment variables, optionally masking encrypted values."""
        sk = self._scope_key(extension_id, org_id)
        result = []
        for var in self._vars.get(sk, {}).values():
            entry = {"key": var.key, "scope": var.scope,
                     "encrypted": var.encrypted, "description": var.description}
            entry["value"] = "***" if (var.encrypted and mask_encrypted) else var.value
            result.append(entry)
        return sorted(result, key=lambda v: v["key"])

    def get_runtime_env(self, extension_id: str, org_id: str = "") -> dict[str, str]:
        """Get flat dict for injection into sandbox runtime."""
        merged: dict[str, str] = {}
        # Extension-level vars
        for var in self._vars.get(self._scope_key(extension_id), {}).values():
            merged[var.key] = var.value
        # Org-level overrides
        if org_id:
            for var in self._vars.get(self._scope_key(extension_id, org_id), {}).values():
                merged[var.key] = var.value
        return merged
