"""App signing utilities — content signing and verification.

Uses HMAC-SHA256 for signing app bundles and manifests,
providing integrity verification for the app distribution pipeline.
"""

import hashlib
import hmac
import json


def sign_content(content: bytes, signing_key: str) -> str:
    """Sign content with an HMAC-SHA256 signature."""
    return hmac.new(signing_key.encode(), content, hashlib.sha256).hexdigest()


def verify_content(content: bytes, signature: str, signing_key: str) -> bool:
    """Verify content signature."""
    expected = sign_content(content, signing_key)
    return hmac.compare_digest(expected, signature)


def sign_manifest(manifest: dict, signing_key: str) -> str:
    """Sign a manifest dict deterministically."""
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return sign_content(canonical, signing_key)


def verify_manifest(manifest: dict, signature: str, signing_key: str) -> bool:
    """Verify a manifest signature."""
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return verify_content(canonical, signature, signing_key)


def generate_fingerprint(public_key: str) -> str:
    """Generate a SHA-256 fingerprint from a public key."""
    return hashlib.sha256(public_key.encode()).hexdigest()[:32]
