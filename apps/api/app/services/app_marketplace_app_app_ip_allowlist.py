"""IP allowlist — CIDR-based IP access control."""

import ipaddress
import html


def validate_cidr(*, cidr: str) -> dict:
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        return {"valid": True, "cidr": str(net), "version": net.version,
                "num_hosts": net.num_addresses, "is_single": net.prefixlen == (32 if net.version == 4 else 128)}
    except ValueError as e:
        return {"valid": False, "error": str(e)}


def check_ip(*, ip: str, allowlist: list[str]) -> dict:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return {"allowed": False, "error": "Invalid IP address"}
    for cidr in allowlist:
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            if addr in net:
                return {"allowed": True, "ip": ip, "matched_rule": cidr}
        except ValueError:
            continue
    return {"allowed": False, "ip": ip, "matched_rule": None}


def build_allowlist(*, rules: list[dict]) -> dict:
    items = []
    for r in rules:
        v = validate_cidr(cidr=r.get("cidr", ""))
        items.append({"cidr": r.get("cidr", ""), "label": html.escape(r.get("label", "")),
                       "valid": v.get("valid", False), "num_hosts": v.get("num_hosts", 0)})
    return {"rules": items, "total": len(items),
            "valid_count": sum(1 for i in items if i["valid"])}
