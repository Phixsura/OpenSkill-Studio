"""SBOM generator — generate Software Bill of Materials."""
from __future__ import annotations
import hashlib


def generate_sbom(app_name: str, dependencies: list[dict]) -> dict:
    components = []
    licenses: set[str] = set()
    for dep in dependencies:
        lic = dep.get("license", "unknown")
        licenses.add(lic)
        components.append({"name": dep["name"], "version": dep.get("version", ""),
                           "license": lic, "type": dep.get("type", "library"),
                           "hash": hashlib.sha256(f"{dep['name']}:{dep.get('version', '')}".encode()).hexdigest()[:12]})
    return {"app": app_name, "format": "CycloneDX", "components": components,
            "total_components": len(components), "unique_licenses": sorted(licenses),
            "license_count": len(licenses)}


def check_license_compliance(sbom: dict, banned: list[str]) -> dict:
    violations = []
    for comp in sbom["components"]:
        if comp["license"] in banned:
            violations.append({"component": comp["name"], "license": comp["license"]})
    return {"compliant": len(violations) == 0, "violations": violations,
            "violation_count": len(violations)}
