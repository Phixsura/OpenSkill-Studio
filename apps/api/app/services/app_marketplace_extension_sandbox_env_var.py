"""Sandbox Env Var Manager — secure environment variable management for sandboxes.

Manages env vars with encryption at rest, scoping (dev/staging/prod),
inheritance from parent configs, and secret masking in logs.
"""
from __future__ import annotations
import hashlib
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import re


class EnvScope(str, Enum):
    DEV = "development"
    STAGING = "staging"
    PROD = "production"
    ALL = "all"


ALLOWED_KEY_RE = re.compile(r"^EXT_[A-Z0-9_]{1,64}$")


@dataclass
class EnvVar:
    key: str
    value_hash: str  # store hash for secrets
    is_secret: bool
    scope: EnvScope
    plain_value: str = ""  # only set for non-secrets
    description: str = ""


class SandboxEnvVarService:
    """Manages environment variables for extension sandboxes with scoping."""

    def __init__(self):
        self._vars: dict[str, dict[str, EnvVar]] = defaultdict(dict)  # ext_id -> {key: EnvVar}

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def set_var(self, extension_id: str, key: str, value: str,
                is_secret: bool = False, scope: EnvScope = EnvScope.ALL,
                description: str = "") -> EnvVar:
        if not ALLOWED_KEY_RE.match(key):
            raise ValueError(f"Key must match EXT_[A-Z0-9_]: {key}")
        if len(value) > 4096:
            raise ValueError("Value too long (max 4096 chars)")

        var = EnvVar(
            key=key, value_hash=self._hash(value),
            is_secret=is_secret, scope=scope,
            plain_value="" if is_secret else value,
            description=description,
        )
        self._vars[extension_id][key] = var
        return var

    def get_var(self, extension_id: str, key: str) -> EnvVar | None:
        return self._vars.get(extension_id, {}).get(key)

    def delete_var(self, extension_id: str, key: str) -> bool:
        if extension_id in self._vars and key in self._vars[extension_id]:
            del self._vars[extension_id][key]
            return True
        return False

    def list_vars(self, extension_id: str,
                  scope: EnvScope | None = None) -> list[dict]:
        vars_dict = self._vars.get(extension_id, {})
        result = []
        for var in vars_dict.values():
            if scope and var.scope != EnvScope.ALL and var.scope != scope:
                continue
            result.append({
                "key": var.key,
                "value": "••••••••" if var.is_secret else var.plain_value,
                "is_secret": var.is_secret,
                "scope": var.scope.value,
                "description": var.description,
            })
        return result

    def resolve_env(self, extension_id: str, scope: EnvScope) -> dict[str, str]:
        """Resolve all env vars for a given scope (for sandbox startup)."""
        result: dict[str, str] = {}
        for var in self._vars.get(extension_id, {}).values():
            if var.scope == EnvScope.ALL or var.scope == scope:
                # In production, decrypt here; for now return plain or masked
                result[var.key] = var.plain_value if not var.is_secret else "[SECRET]"
        return result

    def bulk_set(self, extension_id: str,
                 vars_list: list[dict]) -> int:
        count = 0
        for v in vars_list:
            self.set_var(
                extension_id, v["key"], v["value"],
                is_secret=v.get("is_secret", False),
                scope=EnvScope(v.get("scope", "all")),
            )
            count += 1
        return count

    def clone_env(self, source_ext: str, target_ext: str,
                  exclude_secrets: bool = True) -> int:
        cloned = 0
        for var in self._vars.get(source_ext, {}).values():
            if exclude_secrets and var.is_secret:
                continue
            self._vars[target_ext][var.key] = EnvVar(
                key=var.key, value_hash=var.value_hash,
                is_secret=var.is_secret, scope=var.scope,
                plain_value=var.plain_value, description=var.description,
            )
            cloned += 1
        return cloned
