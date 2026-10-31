"""Dependency vulnerability scanner — scan deps for known CVEs."""
from __future__ import annotations

SEVERITY_SCORES = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def scan_dependencies(deps: list[dict]) -> dict:
    vulns = []
    for d in deps:
        for v in d.get("vulnerabilities", []):
            vulns.append({"package": d["name"], "version": d["version"],
                          "cve": v.get("cve", ""), "severity": v.get("severity", "medium"),
                          "fixed_in": v.get("fixed_in", ""),
                          "description": v.get("description", "")})
    by_sev: dict[str, int] = {}
    for v in vulns:
        by_sev[v["severity"]] = by_sev.get(v["severity"], 0) + 1
    risk_score = sum(SEVERITY_SCORES.get(v["severity"], 1) for v in vulns)
    return {"vulnerabilities": vulns, "total": len(vulns), "by_severity": by_sev,
            "risk_score": risk_score, "has_critical": by_sev.get("critical", 0) > 0,
            "packages_scanned": len(deps)}


def get_remediation(vulns: list[dict]) -> list[dict]:
    actions = []
    for v in vulns:
        if v.get("fixed_in"):
            actions.append({"package": v["package"], "action": "upgrade",
                            "from": v.get("version", ""), "to": v["fixed_in"],
                            "priority": SEVERITY_SCORES.get(v["severity"], 1)})
    return sorted(actions, key=lambda a: -a["priority"])
