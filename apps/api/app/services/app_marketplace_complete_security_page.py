"""Complete security page — security dashboard with scans, secrets, and policies."""


def build_complete_security_page(*, app: dict, scan_results: dict, secrets: list[dict],
                                     policies: dict, vulnerabilities: list[dict]) -> dict:
    critical_vulns = sum(1 for v in vulnerabilities if v.get("severity") == "critical")
    return {
        "page_type": "security_dashboard",
        "app": {"id": app["id"], "name": app["name"]},
        "security_score": scan_results.get("score", 0),
        "grade": "A" if scan_results.get("score", 0) >= 90 else "B" if scan_results.get("score", 0) >= 75 else "C" if scan_results.get("score", 0) >= 50 else "F",
        "tabs": [
            {"key": "overview", "title": "Overview", "icon": "🔒"},
            {"key": "scan", "title": "Security Scan", "icon": "🔍", "data": scan_results},
            {"key": "secrets", "title": f"Secrets ({len(secrets)})", "icon": "🔑"},
            {"key": "vulns", "title": f"Vulnerabilities ({len(vulnerabilities)})", "icon": "⚠️",
             "critical": critical_vulns},
            {"key": "policies", "title": "Policies", "icon": "📋"},
        ],
        "needs_attention": critical_vulns > 0,
    }
