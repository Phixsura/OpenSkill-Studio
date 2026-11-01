"""Response header inspector — inspect and validate API response headers."""
from __future__ import annotations


def inspect_headers(headers: dict[str, str], required: list[str] | None = None,
                    security_headers: bool = True) -> dict:
    issues = []
    if required:
        for h in required:
            if h.lower() not in {k.lower() for k in headers}:
                issues.append({"header": h, "issue": "missing_required"})
    if security_headers:
        sec = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
               "Strict-Transport-Security": None, "Content-Security-Policy": None}
        for h, expected in sec.items():
            if h.lower() not in {k.lower() for k in headers}:
                issues.append({"header": h, "issue": "missing_security_header"})
            elif expected and headers.get(h, "") != expected:
                issues.append({"header": h, "issue": f"expected '{expected}'"})
    return {"headers_count": len(headers), "issues": issues,
            "secure": len([i for i in issues if "security" in i["issue"]]) == 0,
            "valid": len(issues) == 0}
