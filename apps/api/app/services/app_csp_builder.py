"""CSP builder — generate Content-Security-Policy for sandboxed iframes."""

def build_extension_csp(*, app_slug: str, allowed_hosts: list[str] | None = None) -> str:
    hosts = " ".join(allowed_hosts or [])
    return "; ".join([
        "default-src 'none'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        f"connect-src 'self' https://api.openskill.studio {hosts}".strip(),
        "img-src 'self' data: https:",
        "font-src 'self' https://fonts.gstatic.com",
        "frame-ancestors https://app.openskill.studio",
    ])
