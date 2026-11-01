"""Secret Vault — hierarchical secret storage with versioning and ACL.

HashiCorp Vault-style: path-based secret storage with access policies.

Implements:
- Path-based secrets (apps/myapp/db_password)
- Secret versioning (keep history, rollback)
- Access policies (path patterns → allowed operations)
- Lease-based secrets (auto-expire after TTL)
- Audit log of all access
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import secrets as _secrets


@dataclass
class SecretVersion:
    version: int
    value: str
    created_at: float
    created_by: str
    destroyed: bool = False


@dataclass
class VaultSecret:
    path: str
    versions: list[SecretVersion] = field(default_factory=list)
    lease_ttl: float = 0  # 0 = no lease
    lease_expires: float = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class AccessPolicy:
    name: str
    path_pattern: str  # "apps/*", "apps/myapp/db_*"
    capabilities: set[str] = field(default_factory=set)  # read, write, delete, list


class SecretVaultService:
    def __init__(self, root_token: str = "root"):
        self._secrets: dict[str, VaultSecret] = {}
        self._policies: dict[str, list[AccessPolicy]] = {}
        self._root_tokens: set[str] = {root_token}
        self._audit: list[dict] = []

    def _check_access(self, token: str, path: str, capability: str) -> bool:
        if token in self._root_tokens:
            return True
        policies = self._policies.get(token, [])
        if not policies:
            return False  # deny by default
        for policy in policies:
            if self._path_matches(policy.path_pattern, path):
                if capability in policy.capabilities:
                    return True
        return False

    def _path_matches(self, pattern: str, path: str) -> bool:
        if pattern == path:
            return True
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return False

    def _audit_log(self, op: str, path: str, token: str, success: bool) -> None:
        self._audit.append({"operation": op, "path": path,
                            "token": token[:8] + "..." if len(token) > 8 else token,
                            "success": success, "timestamp": time.time()})

    def write(self, path: str, value: str, token: str = "root",
              metadata: dict | None = None, lease_ttl: float = 0) -> dict:
        """Write a secret (creates new version)."""
        if not self._check_access(token, path, "write"):
            self._audit_log("write", path, token, False)
            raise PermissionError(f"Access denied: write on {path}")

        secret = self._secrets.get(path)
        if not secret:
            secret = VaultSecret(path=path, metadata=metadata or {})
            self._secrets[path] = secret

        version = len(secret.versions) + 1
        sv = SecretVersion(version=version, value=value,
                           created_at=time.time(), created_by=token)
        secret.versions.append(sv)

        if lease_ttl > 0:
            secret.lease_ttl = lease_ttl
            secret.lease_expires = time.time() + lease_ttl

        self._audit_log("write", path, token, True)
        return {"path": path, "version": version}

    def read(self, path: str, token: str = "root",
             version: int = 0) -> dict | None:
        """Read a secret (latest or specific version)."""
        if not self._check_access(token, path, "read"):
            self._audit_log("read", path, token, False)
            raise PermissionError(f"Access denied: read on {path}")

        secret = self._secrets.get(path)
        if not secret:
            self._audit_log("read", path, token, False)
            return None

        # Lease check
        if secret.lease_expires > 0 and time.time() > secret.lease_expires:
            del self._secrets[path]
            return None

        if version > 0:
            sv = next((v for v in secret.versions if v.version == version), None)
        else:
            sv = secret.versions[-1] if secret.versions else None

        if not sv or sv.destroyed:
            return None

        self._audit_log("read", path, token, True)
        return {"path": path, "value": sv.value, "version": sv.version,
                "metadata": secret.metadata}

    def delete(self, path: str, token: str = "root") -> bool:
        """Soft delete latest version (mark as destroyed)."""
        if not self._check_access(token, path, "delete"):
            self._audit_log("delete", path, token, False)
            raise PermissionError("Access denied")
        secret = self._secrets.get(path)
        if secret and secret.versions:
            secret.versions[-1].destroyed = True
            self._audit_log("delete", path, token, True)
            return True
        return False

    def list_paths(self, prefix: str, token: str = "root") -> list[str]:
        if not self._check_access(token, prefix + "*", "list"):
            return []
        return sorted(p for p in self._secrets if p.startswith(prefix))

    def create_policy(self, token: str, policy: AccessPolicy) -> None:
        if token not in self._policies:
            self._policies[token] = []
        self._policies[token].append(policy)

    def get_versions(self, path: str) -> list[dict]:
        secret = self._secrets.get(path)
        if not secret:
            return []
        return [{"version": v.version, "created_at": v.created_at,
                 "destroyed": v.destroyed} for v in secret.versions]

    def get_audit_log(self, path: str = "", limit: int = 50) -> list[dict]:
        entries = self._audit
        if path:
            entries = [e for e in entries if e["path"] == path]
        return entries[-limit:]
