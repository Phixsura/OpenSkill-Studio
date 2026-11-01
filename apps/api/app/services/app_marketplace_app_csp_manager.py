"""CSP manager — build and validate Content Security Policy headers."""


DEFAULT_DIRECTIVES = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "frame-ancestors": ["'none'"],
}


def build_csp(*, directives: dict | None = None, report_uri: str | None = None) -> dict:
    merged = {**DEFAULT_DIRECTIVES, **(directives or {})}
    parts = []
    for directive, sources in sorted(merged.items()):
        parts.append(f"{directive} {' '.join(sources)}")
    if report_uri:
        parts.append(f"report-uri {report_uri}")
    header = "; ".join(parts)
    return {
        "header_name": "Content-Security-Policy",
        "header_value": header,
        "directives": merged,
        "directive_count": len(merged),
    }


def validate_csp(*, header: str) -> dict:
    warnings = []
    if "'unsafe-inline'" in header and "script-src" in header:
        warnings.append("unsafe-inline in script-src weakens XSS protection")
    if "'unsafe-eval'" in header:
        warnings.append("unsafe-eval allows dynamic code execution")
    if "frame-ancestors" not in header:
        warnings.append("Missing frame-ancestors (clickjacking protection)")
    if "*" in header:
        warnings.append("Wildcard source (*) is overly permissive")
    return {
        "valid": True,
        "warnings": warnings,
        "warning_count": len(warnings),
        "security_score": max(100 - len(warnings) * 20, 0),
    }
