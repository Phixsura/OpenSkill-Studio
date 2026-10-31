"""Sandbox isolation checker — verify sandbox config meets security requirements."""

REQUIRED_ISOLATION = {
    "no_network_by_default": True,
    "no_filesystem_write": True,
    "memory_limit_enforced": True,
    "timeout_enforced": True,
    "no_host_access": True,
}


def check_isolation(config: dict) -> dict:
    """Check if sandbox config meets isolation requirements."""
    issues = []
    
    network = config.get("network", {})
    if network.get("egress_policy") not in ("deny", "allowlist"):
        issues.append("Network egress must be deny or allowlist")
    
    if config.get("memory_mb", 0) <= 0:
        issues.append("Memory limit must be set")
    
    if config.get("timeout_seconds", 0) <= 0:
        issues.append("Timeout must be set")
    
    if config.get("privileged"):
        issues.append("Privileged mode not allowed")
    
    if config.get("mount_host_paths"):
        issues.append("Host path mounting not allowed")
    
    return {"isolated": len(issues) == 0, "issues": issues, "checks": len(REQUIRED_ISOLATION)}
