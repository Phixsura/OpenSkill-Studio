"""IP allowlist — restrict API access to specific IP ranges."""

import ipaddress


def validate_ip_entry(*, entry: str) -> dict:
    try:
        network = ipaddress.ip_network(entry, strict=False)
        return {"valid": True, "entry": entry, "normalized": str(network),
                "version": network.version, "num_addresses": network.num_addresses}
    except ValueError as e:
        return {"valid": False, "entry": entry, "error": str(e)}


def check_ip_allowed(*, client_ip: str, allowlist: list[str]) -> dict:
    if not allowlist:
        return {"allowed": True, "reason": "No allowlist configured (all allowed)"}
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return {"allowed": False, "reason": f"Invalid IP: {client_ip}"}
    for entry in allowlist:
        try:
            network = ipaddress.ip_network(entry, strict=False)
            if addr in network:
                return {"allowed": True, "matched_rule": entry}
        except ValueError:
            continue
    return {"allowed": False, "reason": "IP not in allowlist"}


def get_allowlist_summary(*, entries: list[str]) -> dict:
    valid = []
    invalid = []
    for e in entries:
        r = validate_ip_entry(entry=e)
        if r["valid"]:
            valid.append(r)
        else:
            invalid.append(r)
    total_addresses = sum(v["num_addresses"] for v in valid)
    return {"total_rules": len(entries), "valid_rules": len(valid),
            "invalid_rules": len(invalid), "total_addresses": total_addresses}
