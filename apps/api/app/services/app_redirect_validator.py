"""Redirect URI validator — validate OAuth redirect URIs."""

from urllib.parse import urlparse

def validate_redirect_uri(uri: str, registered_uris: list[str]) -> dict:
    """Validate a redirect URI against registered URIs."""
    if not uri:
        return {"valid": False, "error": "Redirect URI is required"}
    if uri not in registered_uris:
        return {"valid": False, "error": "Redirect URI not registered"}
    try:
        parsed = urlparse(uri)
        if parsed.scheme not in ("http", "https"):
            return {"valid": False, "error": "Only HTTP(S) redirect URIs allowed"}
        if parsed.fragment:
            return {"valid": False, "error": "Redirect URI must not contain fragment"}
    except Exception:
        return {"valid": False, "error": "Invalid URI format"}
    return {"valid": True}
