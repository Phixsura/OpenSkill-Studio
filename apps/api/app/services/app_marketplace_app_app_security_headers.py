"""Security headers — generate and validate HTTP security headers."""


RECOMMENDED_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def generate_security_headers(*, custom: dict | None = None) -> dict:
    headers = {**RECOMMENDED_HEADERS, **(custom or {})}
    return {"headers": headers, "total": len(headers)}


def audit_security_headers(*, current_headers: dict) -> dict:
    findings = []
    for header, recommended in RECOMMENDED_HEADERS.items():
        current = current_headers.get(header)
        if not current:
            findings.append({"header": header, "status": "missing", "severity": "high",
                              "recommendation": f"Add: {recommended}"})
        elif current != recommended:
            findings.append({"header": header, "status": "weak", "severity": "medium",
                              "current": current, "recommendation": recommended})
    present = sum(1 for h in RECOMMENDED_HEADERS if h in current_headers)
    score = round(present / len(RECOMMENDED_HEADERS) * 100)
    return {"findings": findings, "score": score,
            "present": present, "total_recommended": len(RECOMMENDED_HEADERS),
            "grade": "A" if score == 100 else "B" if score >= 80 else "C" if score >= 50 else "F"}
