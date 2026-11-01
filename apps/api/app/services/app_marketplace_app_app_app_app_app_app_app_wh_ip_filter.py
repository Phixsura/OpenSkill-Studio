"""Webhook IP allowlist — filter webhook delivery by source IP."""
from __future__ import annotations
import ipaddress


def validate_ip_list(ips: list[str]) -> dict:
    valid = []
    invalid = []
    for ip in ips:
        try:
            ipaddress.ip_network(ip, strict=False)
            valid.append(ip)
        except ValueError:
            invalid.append(ip)
    return {"valid": valid, "invalid": invalid, "all_valid": len(invalid) == 0}


def check_ip_allowed(ip: str, allowlist: list[str]) -> dict:
    if not allowlist:
        return {"allowed": True, "reason": "no_filter"}
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return {"allowed": False, "reason": "invalid_ip"}
    for cidr in allowlist:
        try:
            if addr in ipaddress.ip_network(cidr, strict=False):
                return {"allowed": True, "matched": cidr}
        except ValueError:
            continue
    return {"allowed": False, "reason": "not_in_allowlist"}


def get_platform_ips() -> list[str]:
    return ["203.0.113.0/24", "198.51.100.0/24", "192.0.2.0/24"]
