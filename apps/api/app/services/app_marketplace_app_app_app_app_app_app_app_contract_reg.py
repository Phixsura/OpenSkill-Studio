"""Service contract registry — register and verify service contracts."""
from __future__ import annotations
import hashlib


def register_contract(provider: str, consumer: str, version: str, schema: dict) -> dict:
    contract_id = hashlib.sha256(f"{provider}:{consumer}:{version}".encode()).hexdigest()[:10]
    return {"contract_id": contract_id, "provider": provider, "consumer": consumer,
            "version": version, "schema": schema, "field_count": len(schema.get("fields", [])),
            "status": "active"}


def verify_contract(contract: dict, actual_response: dict) -> dict:
    fields = contract["schema"].get("fields", [])
    missing = [f for f in fields if f not in actual_response]
    extra = [k for k in actual_response if k not in fields and k != "_meta"]
    return {"contract_id": contract["contract_id"], "valid": len(missing) == 0,
            "missing_fields": missing, "extra_fields": extra,
            "compliance_pct": round((len(fields) - len(missing)) / max(len(fields), 1) * 100)}


def contract_summary(contracts: list[dict]) -> dict:
    by_provider: dict[str, int] = {}
    for c in contracts:
        by_provider[c["provider"]] = by_provider.get(c["provider"], 0) + 1
    return {"total": len(contracts), "providers": sorted(by_provider.keys()),
            "by_provider": by_provider}
