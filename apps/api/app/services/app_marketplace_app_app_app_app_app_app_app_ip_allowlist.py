"""IP allowlist — restrict API access by IP address."""
from __future__ import annotations
import ipaddress


def validate_ip(addr: str) -> dict:
    try:
        ip = ipaddress.ip_address(addr)
        return {"valid": True, "address": str(ip), "version": ip.version,
                "is_private": ip.is_private, "is_loopback": ip.is_loopback}
    except ValueError:
        try:
            net = ipaddress.ip_network(addr, strict=False)
            return {"valid": True, "network": str(net), "version": net.version,
                    "num_addresses": net.num_addresses}
        except ValueError:
            return {"valid": False, "error": "invalid_ip_or_cidr"}


def check_access(allowlist: list[str], client_ip: str) -> dict:
    if not allowlist:
        return {"allowed": True, "reason": "no_restrictions"}
    try:
        client = ipaddress.ip_address(client_ip)
    except ValueError:
        return {"allowed": False, "reason": "invalid_client_ip"}
    for entry in allowlist:
        try:
            net = ipaddress.ip_network(entry, strict=False)
            if client in net:
                return {"allowed": True, "matched_rule": entry}
        except ValueError:
            continue
    return {"allowed": False, "reason": "not_in_allowlist"}


def summarize_allowlist(entries: list[str]) -> dict:
    valid = []
    invalid = []
    for e in entries:
        r = validate_ip(e)
        if r["valid"]:
            valid.append(e)
        else:
            invalid.append(e)
    return {"total": len(entries), "valid": len(valid),
            "invalid": len(invalid), "invalid_entries": invalid}
