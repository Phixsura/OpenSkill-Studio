"""Credential signing service — Ed25519 keypair management and DID:web (ADR-015 D-VC).

Provides:
  - Ed25519 keypair generation per organization
  - Payload signing and verification
  - DID:web document construction
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.signing import OrgSigningKey


def generate_keypair() -> tuple[str, str]:
    """Generate an Ed25519 keypair.

    Returns (private_key_pem, public_key_pem) as PEM strings.
    """
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return private_pem, public_pem


def sign_payload(payload_json: str, private_key_pem: str) -> str:
    """Sign a JSON payload with Ed25519.

    Returns the signature as a base64url-encoded string (no padding).
    """
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    private_key = load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Key is not an Ed25519 private key")
    signature = private_key.sign(payload_json.encode("utf-8"))
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def verify_signature(payload_json: str, signature_b64: str, public_key_pem: str) -> bool:
    """Verify an Ed25519 signature.

    Returns True if valid, False otherwise.
    """
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    try:
        public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        # Re-pad the base64url signature
        padded = signature_b64 + "=" * (-len(signature_b64) % 4)
        sig_bytes = base64.urlsafe_b64decode(padded)
        public_key.verify(sig_bytes, payload_json.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


def compute_payload_hash(payload_json: str) -> str:
    """SHA-256 hash of a payload string."""
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def public_key_to_multibase(public_key_pem: str) -> str:
    """Convert a PEM public key to multibase (base58btc) for DID documents.

    Uses base64url encoding with 'z' prefix (simplified multibase).
    """
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
    raw_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    # Multicodec prefix for Ed25519 public key: 0xed01
    prefixed = b"\xed\x01" + raw_bytes
    return "z" + base64.urlsafe_b64encode(prefixed).decode("ascii").rstrip("=")


def build_did_document(org_id: str, public_key_pem: str) -> dict:
    """Build a DID:web document for an organization.

    DID format: did:web:openskill.studio:orgs:{org_id}
    """
    did = f"did:web:openskill.studio:orgs:{org_id}"
    multibase_key = public_key_to_multibase(public_key_pem)

    return {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
        "id": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": multibase_key,
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
    }


# ---------------------------------------------------------------------------
# DB-backed key management
# ---------------------------------------------------------------------------


class SigningKeyService:
    """Manages Ed25519 signing keys per organization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_active_key(self, org_id: str) -> OrgSigningKey:
        """Get the active signing key for an org, creating one if none exists."""
        result = await self.db.execute(
            select(OrgSigningKey).where(
                OrgSigningKey.org_id == org_id,
                OrgSigningKey.status == "active",
            )
        )
        key = result.scalar_one_or_none()
        if key:
            return key

        private_pem, public_pem = generate_keypair()
        key = OrgSigningKey(
            org_id=org_id,
            key_type="ed25519",
            public_key=public_pem,
            private_key_encrypted=private_pem,  # TODO: encrypt with app secret
        )
        self.db.add(key)
        await self.db.flush()
        return key

    async def get_key(self, key_id: str) -> OrgSigningKey | None:
        """Execute get key."""
        return await self.db.get(OrgSigningKey, key_id)

    async def get_active_key_for_org(self, org_id: str) -> OrgSigningKey | None:
        """Execute get active key for org."""
        result = await self.db.execute(
            select(OrgSigningKey).where(
                OrgSigningKey.org_id == org_id,
                OrgSigningKey.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def rotate_key(self, org_id: str) -> OrgSigningKey:
        """Rotate the active key: mark old as rotated, create new."""
        from datetime import UTC, datetime

        old_key = await self.get_active_key_for_org(org_id)
        if old_key:
            old_key.status = "rotated"
            old_key.rotated_at = datetime.now(UTC)

        private_pem, public_pem = generate_keypair()
        new_key = OrgSigningKey(
            org_id=org_id,
            key_type="ed25519",
            public_key=public_pem,
            private_key_encrypted=private_pem,
        )
        self.db.add(new_key)
        await self.db.flush()
        return new_key

    async def revoke_key(self, key_id: str) -> OrgSigningKey | None:
        """Execute revoke key."""
        key = await self.db.get(OrgSigningKey, key_id)
        if not key:
            return None
        key.status = "revoked"
        await self.db.flush()
        return key
