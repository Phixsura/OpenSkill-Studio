"""Data encryption manager — manage encryption keys and data-at-rest encryption."""
from __future__ import annotations
import hashlib, secrets


class DataEncryptionManager:
    def __init__(self):
        self._keys: dict[str, dict] = {}
        self._active_key: str | None = None

    def create_key(self, name: str, algorithm: str = "AES-256-GCM") -> dict:
        key_material = secrets.token_hex(32)
        fingerprint = hashlib.sha256(key_material.encode()).hexdigest()[:16]
        self._keys[name] = {"name": name, "algorithm": algorithm,
                             "fingerprint": fingerprint, "status": "active",
                             "version": 1}
        if not self._active_key:
            self._active_key = name
        return {"name": name, "fingerprint": fingerprint, "algorithm": algorithm}

    def rotate_key(self, name: str) -> dict:
        if name not in self._keys:
            return {"rotated": False, "error": "key_not_found"}
        key = self._keys[name]
        new_material = secrets.token_hex(32)
        key["fingerprint"] = hashlib.sha256(new_material.encode()).hexdigest()[:16]
        key["version"] += 1
        return {"name": name, "version": key["version"], "new_fingerprint": key["fingerprint"]}

    def set_active(self, name: str) -> dict:
        if name not in self._keys:
            return {"success": False}
        self._active_key = name
        return {"active_key": name, "success": True}

    def stats(self) -> dict:
        return {"total_keys": len(self._keys), "active_key": self._active_key,
                "keys": [{"name": k["name"], "version": k["version"],
                          "fingerprint": k["fingerprint"]} for k in self._keys.values()]}
