"""Extension API Key Rotation — manage API keys with scheduled rotation."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import time


@dataclass
class ApiKey:
    key_id: str
    prefix: str  # first 8 chars for display
    hashed_key: str
    extension_id: str
    name: str
    scopes: list[str] = field(default_factory=list)
    created_at: float = 0.0
    expires_at: float = 0.0
    last_used: float = 0.0
    active: bool = True
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtApiKeyRotationService:
    def __init__(self):
        self._keys: dict[str, ApiKey] = {}  # key_id -> key
        self._lookup: dict[str, str] = {}  # hashed -> key_id
        self._counter = 0

    def _hash(self, raw: str) -> str:
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()

    def create(self, extension_id: str, name: str, scopes: list[str],
               ttl_days: int = 90) -> tuple[str, ApiKey]:
        self._counter += 1
        raw_key = f"osk_{secrets.token_urlsafe(32)}"
        hashed = self._hash(raw_key)
        key = ApiKey(key_id=f"key-{self._counter}", prefix=raw_key[:12],
                     hashed_key=hashed, extension_id=extension_id,
                     name=name, scopes=scopes,
                     expires_at=time.time() + ttl_days * 86400)
        self._keys[key.key_id] = key
        self._lookup[hashed] = key.key_id
        return raw_key, key

    def validate(self, raw_key: str) -> ApiKey | None:
        hashed = self._hash(raw_key)
        key_id = self._lookup.get(hashed)
        if not key_id: return None
        key = self._keys.get(key_id)
        if not key or not key.active: return None
        if key.expires_at != 0 and time.time() > key.expires_at:
            key.active = False
            return None
        key.last_used = time.time()
        return key

    def rotate(self, key_id: str, grace_hours: int = 24) -> tuple[str, ApiKey] | None:
        old = self._keys.get(key_id)
        if not old or not old.active: return None
        old.expires_at = time.time() + grace_hours * 3600
        raw, new_key = self.create(old.extension_id, old.name, old.scopes)
        return raw, new_key

    def revoke(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if key:
            key.active = False
            return True
        return False

    def list_keys(self, extension_id: str) -> list[ApiKey]:
        return [k for k in self._keys.values() if k.extension_id == extension_id and k.active]
