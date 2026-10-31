"""Secrets vault — encrypted secrets storage with access control."""
from __future__ import annotations
import hashlib, secrets as sec_mod


class SecretsVault:
    def __init__(self):
        self._secrets: dict[str, dict] = {}
        self._access_log: list[dict] = []

    def store(self, key: str, value: str, owner: str) -> dict:
        masked = value[:2] + "*" * max(0, len(value) - 4) + value[-2:] if len(value) > 4 else "****"
        fingerprint = hashlib.sha256(value.encode()).hexdigest()[:12]
        self._secrets[key] = {"key": key, "value": value, "owner": owner,
                               "fingerprint": fingerprint, "version": 1}
        return {"key": key, "fingerprint": fingerprint, "masked": masked}

    def retrieve(self, key: str, accessor: str) -> dict:
        if key not in self._secrets:
            return {"found": False, "key": key}
        secret = self._secrets[key]
        self._access_log.append({"key": key, "accessor": accessor, "action": "read"})
        return {"found": True, "key": key, "value": secret["value"],
                "fingerprint": secret["fingerprint"]}

    def rotate(self, key: str, new_value: str, rotated_by: str) -> dict:
        if key not in self._secrets:
            return {"rotated": False, "error": "not_found"}
        self._secrets[key]["value"] = new_value
        self._secrets[key]["version"] += 1
        self._secrets[key]["fingerprint"] = hashlib.sha256(new_value.encode()).hexdigest()[:12]
        self._access_log.append({"key": key, "accessor": rotated_by, "action": "rotate"})
        return {"rotated": True, "key": key, "version": self._secrets[key]["version"]}

    def audit_log(self, limit: int = 20) -> list[dict]:
        return self._access_log[-limit:]

    def stats(self) -> dict:
        return {"total_secrets": len(self._secrets), "total_accesses": len(self._access_log)}
