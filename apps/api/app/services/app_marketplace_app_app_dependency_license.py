"""Dependency license — scan and report licenses of all dependencies."""


LICENSE_COMPATIBILITY = {
    "MIT": {"risk": "low", "commercial": True, "copyleft": False},
    "Apache-2.0": {"risk": "low", "commercial": True, "copyleft": False},
    "BSD-3-Clause": {"risk": "low", "commercial": True, "copyleft": False},
    "ISC": {"risk": "low", "commercial": True, "copyleft": False},
    "GPL-3.0": {"risk": "high", "commercial": False, "copyleft": True},
    "LGPL-3.0": {"risk": "medium", "commercial": True, "copyleft": True},
    "AGPL-3.0": {"risk": "critical", "commercial": False, "copyleft": True},
    "MPL-2.0": {"risk": "medium", "commercial": True, "copyleft": True},
    "Unlicense": {"risk": "low", "commercial": True, "copyleft": False},
}


def scan_licenses(*, dependencies: list[dict]) -> dict:
    results = []
    for dep in dependencies:
        license_id = dep.get("license", "Unknown")
        info = LICENSE_COMPATIBILITY.get(license_id, {"risk": "unknown", "commercial": None, "copyleft": None})
        results.append({"name": dep["name"], "version": dep.get("version", ""),
                         "license": license_id, **info})
    by_risk: dict[str, int] = {}
    for r in results:
        by_risk[r["risk"]] = by_risk.get(r["risk"], 0) + 1
    copyleft_count = sum(1 for r in results if r.get("copyleft"))
    commercial_safe = all(r.get("commercial", True) for r in results if r.get("commercial") is not None)
    return {
        "dependencies": results,
        "total": len(results),
        "by_risk": by_risk,
        "copyleft_count": copyleft_count,
        "commercial_safe": commercial_safe,
        "has_critical": by_risk.get("critical", 0) > 0,
    }
