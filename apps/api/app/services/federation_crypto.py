"""Federation cryptographic primitives — Ed25519 signing, verification, canonical JSON (ADR-017)."""

import hashlib
import json
from datetime import UTC, datetime

import structlog
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from ulid import ULID

log = structlog.get_logger()


# ── Key generation ───────────────────────────────────────


def generate_ed25519_keypair() -> tuple[str, str, str]:
    """Generate an Ed25519 keypair.

    Returns (private_key_pem, public_key_pem, key_id).
    key_id is SHA-256 fingerprint of the DER-encoded public key: "sha256:<hex>".
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    # Fingerprint from raw DER public key bytes
    public_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    key_id = "sha256:" + hashlib.sha256(public_der).hexdigest()

    return private_pem, public_pem, key_id


def compute_key_id(public_key_pem: str) -> str:
    """Compute key_id from a PEM-encoded public key."""
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    public_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return "sha256:" + hashlib.sha256(public_der).hexdigest()


# ── Canonical JSON ───────────────────────────────────────


def canonical_json(obj: dict) -> bytes:
    """Deterministic JSON serialization for signing.

    Keys sorted lexicographically at every nesting level.
    No trailing commas, no whitespace. UTF-8 encoded.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")


def _json_default(o: object) -> str:
    """Handle datetime and other non-JSON-native types."""
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


# ── Signing ──────────────────────────────────────────────


def sign_envelope(payload: dict, envelope_type: str, instance_uri: str,
                  signing_key_pem: str, key_id: str,
                  expires_at: datetime | None = None) -> dict:
    """Build and sign a federation envelope.

    Returns the full envelope dict including the base64url signature.
    """
    import base64

    envelope = {
        "envelope_version": "1.0",
        "envelope_id": str(ULID()),
        "envelope_type": envelope_type,
        "source_instance": instance_uri,
        "source_key_id": key_id,
        "issued_at": datetime.now(UTC).isoformat(),
        "payload": payload,
    }
    if expires_at is not None:
        envelope["expires_at"] = expires_at.isoformat()

    # Sign canonical form (without signature field)
    message = canonical_json(envelope)
    private_key = serialization.load_pem_private_key(signing_key_pem.encode(), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Signing key must be Ed25519")

    sig_bytes = private_key.sign(message)
    envelope["signature"] = base64.urlsafe_b64encode(sig_bytes).decode()

    return envelope


# ── Verification ─────────────────────────────────────────


def verify_envelope_signature(envelope: dict, public_key_pem: str) -> bool:
    """Verify an envelope's Ed25519 signature.

    envelope must contain a 'signature' field. Verification is performed
    on the canonical JSON of the envelope WITHOUT the signature field.
    """
    import base64

    signature_b64 = envelope.get("signature")
    if not signature_b64:
        return False

    try:
        sig_bytes = base64.urlsafe_b64decode(signature_b64)
    except Exception:
        log.warning("federation.invalid_base64_signature")
        return False

    # Build the message that was signed (envelope without signature)
    envelope_copy = {k: v for k, v in envelope.items() if k != "signature"}
    message = canonical_json(envelope_copy)

    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        if not isinstance(public_key, Ed25519PublicKey):
            log.warning("federation.not_ed25519_public_key")
            return False
        public_key.verify(sig_bytes, message)
        return True
    except Exception:
        log.warning("federation.signature_verification_failed")
        return False


def verify_envelope_with_peer(
    envelope: dict,
    peer_key_id: str,
    peer_public_key_pem: str,
    peer_previous_key_id: str | None = None,
    peer_previous_key_pem: str | None = None,
    peer_previous_key_expires_at: datetime | None = None,
) -> bool:
    """Verify an envelope against a peer's current or previous key.

    Tries current key first; falls back to previous key within grace period.
    """
    source_key_id = envelope.get("source_key_id")
    if not source_key_id:
        return False

    # Try current key
    if source_key_id == peer_key_id:
        return verify_envelope_signature(envelope, peer_public_key_pem)

    # Try previous key within grace period
    if (
        peer_previous_key_id
        and source_key_id == peer_previous_key_id
        and peer_previous_key_pem
        and peer_previous_key_expires_at
        and peer_previous_key_expires_at > datetime.now(UTC)
    ):
        return verify_envelope_signature(envelope, peer_previous_key_pem)

    return False
