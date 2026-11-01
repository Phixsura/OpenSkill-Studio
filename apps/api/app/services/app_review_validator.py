"""App review validator — automated pre-review checks.

Runs automated checks before human review:
- Manifest validity
- SSRF-safe network hosts
- No excessive permissions
- Version format valid
- Content hash present
"""

from app.services.manifest_validator import validate_manifest
from app.services.app_compatibility import parse_semver

MAX_PERMISSIONS = 20
HIGH_RISK_PERMISSIONS = frozenset({"write:settings", "write:evaluations", "run:background_jobs"})


def run_automated_review(*, manifest: dict, content_hash: str | None, version: str) -> dict:
    """Run automated review checks.
    
    Returns {"passed": bool, "checks": [...], "score": int}
    """
    checks = []

    # 1. Manifest validation
    result = validate_manifest(manifest)
    checks.append({
        "name": "manifest_valid",
        "passed": result.valid,
        "message": "Valid manifest" if result.valid else f"Invalid: {'; '.join(result.errors[:3])}",
    })

    # 2. Version format
    semver = parse_semver(version)
    checks.append({
        "name": "version_format",
        "passed": semver is not None,
        "message": "Valid semver" if semver else f"Invalid version: {version}",
    })

    # 3. Content hash
    checks.append({
        "name": "content_hash",
        "passed": bool(content_hash and len(content_hash) == 64),
        "message": "Valid content hash" if content_hash and len(content_hash) == 64 else "Missing or invalid content hash",
    })

    # 4. Permission count
    perms = manifest.get("permissions", [])
    checks.append({
        "name": "permission_count",
        "passed": len(perms) <= MAX_PERMISSIONS,
        "message": f"{len(perms)} permissions" if len(perms) <= MAX_PERMISSIONS else f"Too many permissions ({len(perms)} > {MAX_PERMISSIONS})",
    })

    # 5. High-risk permissions
    high_risk = [p for p in perms if p in HIGH_RISK_PERMISSIONS]
    checks.append({
        "name": "high_risk_permissions",
        "passed": True,  # Warning only
        "message": f"High-risk: {', '.join(high_risk)}" if high_risk else "No high-risk permissions",
        "warning": bool(high_risk),
    })

    passed = all(c["passed"] for c in checks)
    score = int(sum(1 for c in checks if c["passed"]) / len(checks) * 100)

    return {"passed": passed, "checks": checks, "score": score}
