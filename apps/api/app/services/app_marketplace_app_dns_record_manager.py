"""DNS record manager — manage DNS records for app domains."""

import re

RECORD_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "SRV"}
IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


def create_dns_record(*, domain: str, record_type: str, name: str,
                        value: str, ttl: int = 300) -> dict:
    if record_type not in RECORD_TYPES:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(RECORD_TYPES))}"}
    if record_type == "A" and not IPV4_RE.match(value):
        return {"error": "A record requires valid IPv4 address"}
    if ttl < 60 or ttl > 86400:
        return {"error": "TTL must be 60-86400 seconds"}
    return {
        "domain": domain, "type": record_type, "name": name,
        "value": value, "ttl": ttl, "status": "active",
        "fqdn": f"{name}.{domain}" if name != "@" else domain,
    }


def list_dns_records(*, domain: str) -> dict:
    return {
        "domain": domain,
        "records": [
            {"type": "A", "name": "@", "value": "93.184.216.34", "ttl": 300},
            {"type": "CNAME", "name": "www", "value": "apps.openskill.dev", "ttl": 3600},
            {"type": "TXT", "name": "@", "value": "v=spf1 include:_spf.openskill.dev ~all", "ttl": 3600},
        ],
        "total": 3,
    }
