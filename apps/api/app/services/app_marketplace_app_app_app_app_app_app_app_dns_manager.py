"""DNS record manager — manage DNS zones and records."""
from __future__ import annotations


class DnsManager:
    def __init__(self):
        self._zones: dict[str, dict] = {}

    def create_zone(self, domain: str) -> dict:
        self._zones[domain] = {"domain": domain, "records": []}
        return {"domain": domain, "status": "created"}

    def add_record(self, domain: str, *, rtype: str, name: str,
                    value: str, ttl: int = 3600) -> dict:
        zone = self._zones.get(domain)
        if not zone:
            return {"error": "Zone not found"}
        if rtype not in ("A", "AAAA", "CNAME", "TXT", "MX", "NS", "SRV"):
            return {"error": f"Invalid type: {rtype}"}
        record = {"type": rtype, "name": name, "value": value, "ttl": ttl}
        zone["records"].append(record)
        return {"added": True, "record": record}

    def remove_record(self, domain: str, *, name: str, rtype: str) -> dict:
        zone = self._zones.get(domain)
        if not zone:
            return {"error": "Zone not found"}
        before = len(zone["records"])
        zone["records"] = [r for r in zone["records"]
                           if not (r["name"] == name and r["type"] == rtype)]
        return {"removed": before > len(zone["records"])}

    def list_records(self, domain: str) -> dict:
        zone = self._zones.get(domain)
        if not zone:
            return {"error": "Zone not found"}
        return {"domain": domain, "records": zone["records"],
                "count": len(zone["records"])}
