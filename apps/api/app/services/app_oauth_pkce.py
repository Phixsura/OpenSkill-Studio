"""OAuth PKCE — code challenge/verifier for public clients."""

import hashlib
import base64
import secrets


def generate_code_verifier() -> str:
    """Generate a random code verifier (43-128 chars)."""
    return secrets.token_urlsafe(64)


def compute_code_challenge(verifier: str) -> str:
    """Compute S256 code challenge from verifier."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def verify_pkce(verifier: str, challenge: str) -> bool:
    """Verify a PKCE code verifier matches the stored challenge."""
    return compute_code_challenge(verifier) == challenge
