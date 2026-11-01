"""License checker — open source license compatibility analysis."""

import html

LICENSES = {
    "MIT": {"spdx": "MIT", "permissive": True, "copyleft": False, "risk": "low"},
    "Apache-2.0": {"spdx": "Apache-2.0", "permissive": True, "copyleft": False, "risk": "low"},
    "BSD-3-Clause": {"spdx": "BSD-3-Clause", "permissive": True, "copyleft": False, "risk": "low"},
    "GPL-3.0": {"spdx": "GPL-3.0-only", "permissive": False, "copyleft": True, "risk": "high"},
    "LGPL-3.0": {"spdx": "LGPL-3.0-only", "permissive": False, "copyleft": True, "risk": "medium"},
    "AGPL-3.0": {"spdx": "AGPL-3.0-only", "permissive": False, "copyleft": True, "risk": "critical"},
    "Unlicense": {"spdx": "Unlicense", "permissive": True, "copyleft": False, "risk": "low"},
    "UNKNOWN": {"spdx": "UNKNOWN", "permissive": False, "copyleft": False, "risk": "critical"},
}


def check_license(*, license_id: str) -> dict:
    info = LICENSES.get(license_id, LICENSES["UNKNOWN"])
    return {"license": license_id, **info}


def audit_dependencies(*, deps: list[dict]) -> dict:
    results = []
    risks = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in deps:
        lic = d.get("license", "UNKNOWN")
        info = check_license(license_id=lic)
        info["package"] = html.escape(d.get("name", ""))
        results.append(info)
        risks[info["risk"]] = risks.get(info["risk"], 0) + 1
    overall = "critical" if risks["critical"] else "high" if risks["high"] else "medium" if risks["medium"] else "low"
    return {"dependencies": results, "total": len(results), "risks": risks,
            "overall_risk": overall, "has_copyleft": any(r["copyleft"] for r in results)}
