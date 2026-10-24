"""Security page FINAL — comprehensive security dashboard for apps."""


def build_security_page_final(*, app: dict, scan: dict, secrets: list[dict],
                                    dependencies: dict, policies: dict,
                                    vulnerabilities: list[dict]) -> dict:
    critical = sum(1 for v in vulnerabilities if v.get("severity") == "critical")
    high = sum(1 for v in vulnerabilities if v.get("severity") == "high")
    score = scan.get("score", 0)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "F"
    return {
        "page_type": "security_page_final",
        "app": {"id": app["id"], "name": app["name"]},
        "overview": {"score": score, "grade": grade, "critical": critical, "high": high,
                      "needs_attention": critical > 0},
        "tabs": [
            {"key": "overview", "title": "Overview", "icon": "🔒"},
            {"key": "scan", "title": "Scan Results", "icon": "🔍", "data": scan},
            {"key": "secrets", "title": f"Secrets ({len(secrets)})", "icon": "🔑"},
            {"key": "deps", "title": "Dependencies", "icon": "📦", "data": dependencies},
            {"key": "vulns", "title": f"Vulnerabilities ({len(vulnerabilities)})", "icon": "⚠️"},
            {"key": "policies", "title": "Policies", "icon": "📋", "data": policies},
        ],
    }
