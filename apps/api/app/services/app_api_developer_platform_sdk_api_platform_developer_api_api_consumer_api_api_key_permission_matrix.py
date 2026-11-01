"""API Consumer API Key Permission Matrix — fine-grained key-to-endpoint permissions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PermissionEntry:
    endpoint: str
    method: str
    allowed: bool = True

@dataclass
class KeyPermissionMatrix:
    key_id: str
    consumer_id: str
    permissions: list[PermissionEntry] = field(default_factory=list)
    default_allow: bool = False  # fail-closed by default

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrix:
    def __init__(self) -> None:
        self._matrices: dict[tuple[str, str], KeyPermissionMatrix] = {}

    def set_matrix(self, installation_id: str, matrix: KeyPermissionMatrix) -> KeyPermissionMatrix:
        if not installation_id: raise ValueError("installation_id is required")
        self._matrices[(installation_id, matrix.key_id)] = matrix
        return matrix

    def check_permission(self, installation_id: str, key_id: str, method: str, endpoint: str) -> bool:
        matrix = self._matrices.get((installation_id, key_id))
        if matrix is None: return False  # fail-closed: unknown key
        for p in matrix.permissions:
            if p.endpoint == endpoint and p.method.upper() == method.upper():
                return p.allowed
        return matrix.default_allow

    def add_permission(self, installation_id: str, key_id: str, endpoint: str, method: str, allowed: bool = True) -> KeyPermissionMatrix:
        matrix = self._matrices.get((installation_id, key_id))
        if matrix is None: raise KeyError(f"Key {key_id} not found")
        matrix.permissions.append(PermissionEntry(endpoint=endpoint, method=method.upper(), allowed=allowed))
        return matrix

    def list_matrices(self, installation_id: str) -> list[KeyPermissionMatrix]:
        return [m for (inst, _), m in self._matrices.items() if inst == installation_id]
