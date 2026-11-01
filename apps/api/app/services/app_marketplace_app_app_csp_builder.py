"""CSP builder — Content Security Policy header generator."""


DEFAULT_DIRECTIVES = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "frame-ancestors": ["'none'"],
    "base-uri": ["'self'"],
    "form-action": ["'self'"],
}


def build_csp(*, overrides: dict[str, list[str]] | None = None,
               report_uri: str | None = None) -> dict:
    directives = {k: list(v) for k, v in DEFAULT_DIRECTIVES.items()}
    if overrides:
        for key, values in overrides.items():
            directives.setdefault(key, []).extend(values)
    parts = [f"{k} {' '.join(v)}" for k, v in sorted(directives.items())]
    header = "; ".join(parts)
    if report_uri:
        header += f"; report-uri {report_uri}"
    return {"header": header, "directives": directives,
            "directive_count": len(directives)}


def analyze_csp(*, header: str) -> dict:
    parts = [p.strip() for p in header.split(";") if p.strip()]
    directives = {}
    warnings = []
    for part in parts:
        tokens = part.split()
        if len(tokens) >= 2:
            directives[tokens[0]] = tokens[1:]
    if "default-src" not in directives:
        warnings.append("Missing default-src directive")
    if "script-src" in directives and "'unsafe-inline'" in directives["script-src"]:
        warnings.append("script-src allows unsafe-inline")
    if "frame-ancestors" not in directives:
        warnings.append("Missing frame-ancestors (clickjacking protection)")
    return {"directives": directives, "directive_count": len(directives),
            "warnings": warnings, "warning_count": len(warnings)}
