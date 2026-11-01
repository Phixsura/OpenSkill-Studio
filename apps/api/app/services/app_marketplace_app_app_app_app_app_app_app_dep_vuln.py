"""Dependency vulnerability scanner — scan deps for known vulnerabilities."""
from __future__ import annotations


def scan_dependencies(deps: list[dict], vuln_db: dict[str, list[dict]]) -> dict:
    findings = []
    for dep in deps:
        name = dep["name"]
        version = dep["version"]
        vulns = vuln_db.get(name, [])
        for v in vulns:
            affected = v.get("affected_versions", [])
            if version in affected or "*" in affected:
                findings.append({"package": name, "version": version,
                                 "cve": v["cve"], "severity": v["severity"],
                                 "fix_version": v.get("fix_version", ""),
                                 "title": v.get("title", "")})
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    return {"findings": findings, "total": len(findings),
            "critical": critical, "high": high,
            "deps_scanned": len(deps), "clean": len(findings) == 0}
