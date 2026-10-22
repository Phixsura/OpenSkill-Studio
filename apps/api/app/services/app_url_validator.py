"""URL validator — shared URL validation for webhooks, redirects, icons."""

import re
from urllib.parse import urlparse

SAFE_SCHEMES = frozenset({"http", "https"})
BLOCKED_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "metadata.google.internal"})
BLOCKED_SUFFIXES = (".localhost", ".internal", ".local")


def validate_url(url: str, *, require_https: bool = False, label: str = "URL") -> list[str]:
    """Validate a URL. Returns list of errors."""
    errors = []
    if not url:
        errors.append(f"{label} is required")
        return errors

    try:
        parsed = urlparse(url)
    except Exception:
        errors.append(f"{label} is not a valid URL")
        return errors

    if parsed.scheme not in SAFE_SCHEMES:
        errors.append(f"{label} must use HTTP(S)")
    elif require_https and parsed.scheme != "https":
        errors.append(f"{label} must use HTTPS")

    host = (parsed.hostname or "").lower()
    if not host:
        errors.append(f"{label} has no hostname")
    elif host in BLOCKED_HOSTS:
        errors.append(f"{label} points to a blocked host")
    elif any(host.endswith(s) for s in BLOCKED_SUFFIXES):
        errors.append(f"{label} points to a local/internal host")

    return errors


def is_safe_redirect_uri(uri: str) -> bool:
    """Check if a redirect URI is safe for OAuth."""
    errors = validate_url(uri, require_https=True, label="Redirect URI")
    return len(errors) == 0
