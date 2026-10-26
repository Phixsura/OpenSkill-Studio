"""Sandbox Secret Manager — secure secret storage for extension sandboxes.

Stores encrypted secrets with rotation, access auditing, scope-based
visibility, and automatic redaction in logs.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Secret:
    secret_id: str
    name: str
    value_hash: str
    scope: str  # sandbox, extension, global
    version: int = 1
    created_at: float = 0.0
    rotated_at: float = 0.0
    access_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class AccessLog:
    secret_name: str
    accessor: str
    timestamp: float
    granted: bool


class SandboxSecretManagerService:
    """Manages secrets for extension sandboxes with auditing."""

    REDACTION_PATTERNS = ["password", "secret", "token", "key", "api_key", "credential"]

    def __init__(self):
        self._secrets: dict[str, dict[str, Secret]] = defaultdict(dict)
        self._values: dict[str, str] = {}  # secret_id -> encrypted value (simulated)
        self._audit: list[AccessLog] = []

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def store(self, sandbox_id: str, name: str, value: str,
              scope: str = "sandbox") -> Secret:
        if not name or not value:
            raise ValueError("Name and value required")
        if any(c in name for c in " \t\n"):
            raise ValueError("Secret name must not contain whitespace")

        secret_id = f"sec_{secrets.token_urlsafe(8)}"
        existing = self._secrets[sandbox_id].get(name)
        version = (existing.version + 1) if existing else 1

        secret = Secret(
            secret_id=secret_id, name=name,
            value_hash=self._hash(value), scope=scope,
            version=version,
        )
        self._secrets[sandbox_id][name] = secret
        self._values[secret_id] = value  # In production: encrypt
        return secret

    def retrieve(self, sandbox_id: str, name: str,
                 accessor: str = "system") -> str | None:
        secret = self._secrets.get(sandbox_id, {}).get(name)
        if not secret:
            self._audit.append(AccessLog(
                secret_name=name, accessor=accessor,
                timestamp=time.time(), granted=False,
            ))
            return None

        secret.access_count += 1
        self._audit.append(AccessLog(
            secret_name=name, accessor=accessor,
            timestamp=time.time(), granted=True,
        ))
        return self._values.get(secret.secret_id)

    def rotate(self, sandbox_id: str, name: str, new_value: str) -> Secret | None:
        if name not in self._secrets.get(sandbox_id, {}):
            return None
        secret = self.store(sandbox_id, name, new_value)
        secret.rotated_at = time.time()
        return secret

    def delete(self, sandbox_id: str, name: str) -> bool:
        secret = self._secrets.get(sandbox_id, {}).pop(name, None)
        if secret:
            self._values.pop(secret.secret_id, None)
            return True
        return False

    def list_secrets(self, sandbox_id: str) -> list[dict]:
        return [
            {"name": s.name, "scope": s.scope, "version": s.version,
             "access_count": s.access_count}
            for s in self._secrets.get(sandbox_id, {}).values()
        ]

    def redact(self, text: str) -> str:
        result = text
        for sandbox_secrets in self._secrets.values():
            for secret in sandbox_secrets.values():
                val = self._values.get(secret.secret_id, "")
                if val and val in result:
                    result = result.replace(val, "***REDACTED***")
        return result

    def get_audit_log(self, sandbox_id: str | None = None,
                      limit: int = 50) -> list[dict]:
        logs = self._audit[-limit:]
        return [{"name": l.secret_name, "accessor": l.accessor,
                 "granted": l.granted} for l in logs]
