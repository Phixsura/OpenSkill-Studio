"""App privacy overview — summarize data access and privacy implications."""


def build_privacy_overview(*, permissions: list[str], has_sandbox: bool, network_hosts: list[str],
                             secrets_count: int, privacy_url: str | None) -> dict:
    data_access = []
    for p in permissions:
        action, resource = p.split(":", 1) if ":" in p else (p, "")
        if action == "read":
            data_access.append({"resource": resource, "access": "read-only"})
        elif action == "write":
            data_access.append({"resource": resource, "access": "read-write"})
    
    return {
        "data_access": data_access,
        "network_access": {"hosts": network_hosts, "has_network": len(network_hosts) > 0},
        "sandbox_isolated": has_sandbox,
        "secrets_stored": secrets_count,
        "privacy_policy": privacy_url,
        "has_privacy_policy": bool(privacy_url),
        "risk_level": "low" if has_sandbox and len(permissions) <= 5 else "medium" if len(permissions) <= 10 else "high",
    }
