"""IP allowlist — restrict app API access to specific IP ranges."""

import ipaddress


def validate_ip_entry(entry: str) -> dict:
    try:
        if "/" in entry:
            net = ipaddress.ip_network(entry, strict=False)
            return {"valid": True, "type": "cidr", "addresses": net.num_addresses}
        else:
            ipaddress.ip_address(entry)
            return {"valid": True, "type": "single", "addresses": 1}
    except ValueError:
        return {"valid": False, "type": None, "addresses": 0}


def check_ip_allowed(*, ip: str, allowlist: list[str]) -> bool:
    if not allowlist:
        return True  # No allowlist = allow all
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for entry in allowlist:
        try:
            if "/" in entry:
                if addr in ipaddress.ip_network(entry, strict=False):
                    return True
            elif str(addr) == entry:
                return True
        except ValueError:
            continue
    return False


def build_allowlist_summary(*, entries: list[str]) -> dict:
    valid = []
    invalid = []
    total_addresses = 0
    for e in entries:
        v = validate_ip_entry(e)
        if v["valid"]:
            valid.append(e)
            total_addresses += v["addresses"]
        else:
            invalid.append(e)
    return {"valid_entries": len(valid), "invalid_entries": invalid,
            "total_addresses_covered": total_addresses}
