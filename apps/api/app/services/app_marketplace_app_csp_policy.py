"""CSP policy — Content Security Policy generator for sandboxed apps."""


def build_csp(*, app_id: str, allowed_origins: list[str], allow_eval: bool = False,
                allow_inline: bool = False) -> dict:
    directives = {
        "default-src": ["'self'"],
        "script-src": ["'self'"] + (["'unsafe-eval'"] if allow_eval else []) + (["'unsafe-inline'"] if allow_inline else []),
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'"] + allowed_origins,
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
    header = "; ".join(f"{k} {' '.join(v)}" for k, v in directives.items())
    return {"app_id": app_id, "directives": directives, "header": header}


def validate_csp_origin(origin: str) -> bool:
    if origin in ("'self'", "'none'", "data:", "blob:", "https:", "http:"):
        return True
    if origin.startswith("https://") or origin.startswith("http://"):
        return True
    return False
