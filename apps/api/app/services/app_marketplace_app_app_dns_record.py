"""DNS record — DNS record management and display."""

import html

RECORD_TYPES = {"A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV"}


def validate_record(*, record_type: str, name: str, value: str, ttl: int = 3600) -> dict:
    errors = []
    if record_type not in RECORD_TYPES:
        errors.append(f"Invalid type: {record_type}")
    if not name.strip():
        errors.append("Name is required")
    if not value.strip():
        errors.append("Value is required")
    if ttl < 60 or ttl > 86400:
        errors.append("TTL must be 60-86400")
    return {"valid": len(errors) == 0, "errors": errors,
            "record": {"type": record_type, "name": html.escape(name),
                        "value": html.escape(value), "ttl": ttl}}


def build_dns_table(*, records: list[dict]) -> dict:
    items = [{"type": r.get("type", "A"), "name": html.escape(r.get("name", "")),
              "value": html.escape(r.get("value", "")), "ttl": r.get("ttl", 3600)}
             for r in records]
    by_type = {}
    for r in items:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    return {"records": items, "total": len(items), "by_type": by_type}
