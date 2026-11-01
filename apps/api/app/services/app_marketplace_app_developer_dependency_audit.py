"""Dependency audit — scan app dependencies for vulnerabilities and updates."""


def audit_dependencies(*, dependencies: list[dict]) -> dict:
    vulnerabilities = []
    outdated = []
    for dep in dependencies:
        if dep.get("has_vulnerability"):
            vulnerabilities.append({"name": dep["name"], "severity": dep.get("severity", "medium"),
                                     "advisory": dep.get("advisory", "")})
        if dep.get("latest_version") and dep.get("current_version") != dep.get("latest_version"):
            outdated.append({"name": dep["name"], "current": dep["current_version"],
                              "latest": dep["latest_version"]})
    return {"total": len(dependencies), "vulnerabilities": vulnerabilities,
            "outdated": outdated, "vuln_count": len(vulnerabilities), "outdated_count": len(outdated),
            "clean": len(vulnerabilities) == 0}


def compute_security_score(*, audit: dict) -> dict:
    score = 100
    for v in audit.get("vulnerabilities", []):
        if v["severity"] == "critical":
            score -= 30
        elif v["severity"] == "high":
            score -= 20
        elif v["severity"] == "medium":
            score -= 10
    score -= len(audit.get("outdated", [])) * 2
    return {"score": max(0, score), "grade": "A" if score >= 90 else "B" if score >= 70 else "C" if score >= 50 else "F"}
