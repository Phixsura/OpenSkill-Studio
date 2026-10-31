"""DNS record manager — manage DNS records for apps."""
from __future__ import annotations
import re

RECORD_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS"}
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z]{2,}$")

_records: list[dict] = []


def add_record(domain: str, record_type: str, value: str, ttl: int = 3600) -> dict:
    d = domain.lower().strip()
    if not DOMAIN_RE.match(d):
        return {"added": False, "error": "invalid_domain"}
    if record_type not in RECORD_TYPES:
        return {"added": False, "error": f"invalid_type, use {sorted(RECORD_TYPES)}"}
    entry = {"domain": d, "type": record_type, "value": value, "ttl": ttl}
    _records.append(entry)
    return {"added": True, **entry}


def list_records(domain: str | None = None) -> list[dict]:
    if domain:
        return [r for r in _records if r["domain"] == domain.lower()]
    return list(_records)


def delete_record(domain: str, record_type: str, value: str) -> dict:
    global _records
    before = len(_records)
    _records = [r for r in _records if not (r["domain"] == domain.lower() and r["type"] == record_type and r["value"] == value)]
    return {"deleted": len(_records) < before}


def clear_records() -> None:
    _records.clear()
