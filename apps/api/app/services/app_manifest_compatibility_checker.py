"""Manifest compatibility checker — check if app works with current platform version."""

PLATFORM_VERSION = "1.0.0"
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
SUPPORTED_RUNTIMES = {"python3.11", "python3.12", "nodejs20", "nodejs22"}


def check_compatibility(manifest: dict) -> dict:
    """Check if a manifest is compatible with the current platform."""
    issues = []
    
    sv = manifest.get("schema_version")
    if sv not in SUPPORTED_SCHEMA_VERSIONS:
        issues.append({"field": "schema_version", "message": f"Unsupported schema version: {sv}", "severity": "error"})
    
    runtime = manifest.get("sandbox", {}).get("runtime")
    if runtime and runtime not in SUPPORTED_RUNTIMES:
        issues.append({"field": "sandbox.runtime", "message": f"Unsupported runtime: {runtime}", "severity": "error"})
    
    min_platform = manifest.get("min_platform_version")
    if min_platform and min_platform > PLATFORM_VERSION:
        issues.append({"field": "min_platform_version", "message": f"Requires platform {min_platform}, current is {PLATFORM_VERSION}", "severity": "error"})
    
    compatible = all(i["severity"] != "error" for i in issues)
    return {"compatible": compatible, "platform_version": PLATFORM_VERSION, "issues": issues}
