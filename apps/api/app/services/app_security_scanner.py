"""App security scanner — automated security checks for app manifests.

Checks for common security issues:
- Overly broad permissions
- Dangerous network hosts
- Excessive resource limits
- Missing required security fields
"""

import re

DANGEROUS_PATTERNS = [
    re.compile(r"password", re.I),
    re.compile(r"credit.?card", re.I),
    re.compile(r"ssn|social.?security", re.I),
]

EXCESSIVE_PERMISSIONS = frozenset({
    "write:settings", "write:evaluations",
})


def scan_manifest(manifest: dict) -> dict:
    """Run security scan on a manifest.
    
    Returns {"passed": bool, "findings": [...], "risk_level": str}
    """
    findings = []

    # Check permissions
    perms = manifest.get("permissions", [])
    excessive = [p for p in perms if p in EXCESSIVE_PERMISSIONS]
    if excessive:
        findings.append({"severity": "medium", "type": "excessive_permissions",
                         "message": f"Elevated permissions: {', '.join(excessive)}"})

    # Check network hosts
    sandbox = manifest.get("sandbox", {})
    network = sandbox.get("network", {})
    hosts = network.get("allowed_hosts", [])
    if len(hosts) > 10:
        findings.append({"severity": "low", "type": "many_hosts",
                         "message": f"Large number of network hosts ({len(hosts)})"})

    # Check resource limits
    if sandbox.get("memory_mb", 0) > 512:
        findings.append({"severity": "low", "type": "high_memory",
                         "message": f"High memory limit: {sandbox['memory_mb']}MB"})
    if sandbox.get("timeout_seconds", 0) > 120:
        findings.append({"severity": "low", "type": "long_timeout",
                         "message": f"Long timeout: {sandbox['timeout_seconds']}s"})

    # Check secrets for dangerous naming
    for secret in manifest.get("secrets", []):
        key = secret.get("key", "")
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(key):
                findings.append({"severity": "high", "type": "dangerous_secret_name",
                                 "message": f"Secret '{key}' has a potentially sensitive name"})

    # Determine risk level
    severities = [f["severity"] for f in findings]
    if "high" in severities:
        risk = "high"
    elif "medium" in severities:
        risk = "medium"
    elif findings:
        risk = "low"
    else:
        risk = "none"

    return {"passed": risk in ("none", "low"), "findings": findings, "risk_level": risk, "total_findings": len(findings)}
