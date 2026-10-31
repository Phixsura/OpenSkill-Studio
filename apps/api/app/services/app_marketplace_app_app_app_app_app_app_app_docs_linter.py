"""API documentation linter — validate API docs for completeness."""
from __future__ import annotations


def lint_endpoint(endpoint: dict) -> dict:
    issues = []
    if not endpoint.get("description"):
        issues.append({"severity": "error", "message": "Missing description"})
    if not endpoint.get("responses"):
        issues.append({"severity": "error", "message": "No response codes documented"})
    if endpoint.get("method") in ("POST", "PUT", "PATCH") and not endpoint.get("request_body"):
        issues.append({"severity": "warning", "message": "No request body documented"})
    params = endpoint.get("parameters", [])
    for p in params:
        if not p.get("description"):
            issues.append({"severity": "warning", "message": f"Parameter '{p.get('name', '')}' lacks description"})
    return {"path": endpoint.get("path", ""), "method": endpoint.get("method", ""),
            "issues": issues, "issue_count": len(issues),
            "errors": sum(1 for i in issues if i["severity"] == "error"),
            "warnings": sum(1 for i in issues if i["severity"] == "warning"),
            "valid": all(i["severity"] != "error" for i in issues)}


def lint_api(endpoints: list[dict]) -> dict:
    results = [lint_endpoint(ep) for ep in endpoints]
    total_issues = sum(r["issue_count"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    valid_count = sum(1 for r in results if r["valid"])
    return {"results": results, "total_endpoints": len(endpoints),
            "valid": valid_count, "invalid": len(endpoints) - valid_count,
            "total_issues": total_issues, "total_errors": total_errors,
            "doc_score": round(valid_count / max(len(endpoints), 1) * 100)}
