"""Dependency security scanner — scan all dependencies for vulnerabilities."""
from __future__ import annotations


def scan_dependencies(deps: list[dict]) -> dict:
    vulns = []
    safe = 0
    for d in deps:
        dep_vulns = d.get("vulnerabilities", [])
        if dep_vulns:
            for v in dep_vulns:
                vulns.append({"package": d["name"], "version": d.get("version", ""),
                               "cve": v.get("cve", ""), "severity": v.get("severity", "medium"),
                               "fixed_in": v.get("fixed_in", "")})
        else:
            safe += 1
    critical = sum(1 for v in vulns if v["severity"] == "critical")
    high = sum(1 for v in vulns if v["severity"] == "high")
    return {"total_deps": len(deps), "safe": safe, "vulnerable": len(deps) - safe,
            "total_vulns": len(vulns), "critical": critical, "high": high,
            "vulns": sorted(vulns, key=lambda v: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(v["severity"], 4)),
            "pass": critical == 0 and high == 0}
