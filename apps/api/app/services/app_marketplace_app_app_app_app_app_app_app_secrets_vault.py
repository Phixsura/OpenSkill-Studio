"""Secrets vault — secure storage for application secrets."""
from __future__ import annotations
import hashlib
import secrets as sec_module
import time

_vault: dict[str, dict] = {}


def store_secret(name: str, value: str, owner: str = "") -> dict:
    encrypted = hashlib.sha256(value.encode()).hexdigest()  # simulated encryption
    _vault[name] = {"name": name, "encrypted_hash": encrypted[:16],
                     "owner": owner, "created_at": time.time(), "version": 1,
                     "accessed": 0}
    return {"stored": True, "name": name, "version": 1}


def access_secret(name: str, accessor: str) -> dict:
    entry = _vault.get(name)
    if not entry:
        return {"found": False, "error": "not_found"}
    entry["accessed"] += 1
    return {"found": True, "name": name, "version": entry["version"],
            "access_count": entry["accessed"]}


def rotate_secret(name: str, new_value: str) -> dict:
    entry = _vault.get(name)
    if not entry:
        return {"rotated": False, "error": "not_found"}
    entry["encrypted_hash"] = hashlib.sha256(new_value.encode()).hexdigest()[:16]
    entry["version"] += 1
    return {"rotated": True, "name": name, "new_version": entry["version"]}


def vault_summary() -> dict:
    total = len(_vault)
    total_accesses = sum(v["accessed"] for v in _vault.values())
    return {"total_secrets": total, "total_accesses": total_accesses}


def clear_vault() -> None:
    _vault.clear()
