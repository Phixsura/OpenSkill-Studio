"""Sandbox network policy — enforce network access rules during execution."""


def build_network_rules(*, egress_policy: str, allowed_hosts: list[str]) -> dict:
    """Build network rules for sandbox execution."""
    if egress_policy == "deny":
        return {"allow_network": False, "allowed_hosts": [], "allow_dns": False}
    if egress_policy == "allowlist":
        return {"allow_network": True, "allowed_hosts": sorted(set(h.lower() for h in allowed_hosts)),
                "allow_dns": True, "policy": "allowlist"}
    # Default: deny all
    return {"allow_network": False, "allowed_hosts": [], "allow_dns": False}


def check_host_allowed(host: str, rules: dict) -> bool:
    """Check if a host is allowed by network rules."""
    if not rules.get("allow_network"):
        return False
    return host.lower() in rules.get("allowed_hosts", [])


def validate_network_config(config: dict) -> list[str]:
    errors = []
    policy = config.get("egress_policy", "")
    if policy not in ("deny", "allowlist"):
        errors.append(f"Invalid egress_policy: {policy}")
    hosts = config.get("allowed_hosts", [])
    if policy == "deny" and hosts:
        errors.append("Cannot specify allowed_hosts with deny policy")
    return errors
