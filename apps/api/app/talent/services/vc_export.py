"""W3C Verifiable Credentials export for Skill Passport snapshots (ADR-015 D-VC).

Implements:
  - W3C VC Data Model v1.1 (https://www.w3.org/TR/vc-data-model/)
  - Ed25519Signature2020 proof suite
  - SkillPassportCredential custom type
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from app.talent.services.credential_signing import (
    sign_payload,
)

# W3C VC contexts
VC_CONTEXT = [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1",
]


def export_passport_as_vc(
    *,
    snapshot_payload: dict,
    snapshot_id: str,
    user_id: str,
    issued_at: datetime,
    expires_at: datetime | None,
    org_id: str,
    org_name: str | None = None,
    signing_key_id: str,
    private_key_pem: str,
    public_key_pem: str,
    checksum: str | None = None,
) -> dict:
    """Export a passport snapshot as a W3C Verifiable Credential.

    Returns a complete VC JSON-LD document with Ed25519Signature2020 proof.
    """
    did = f"did:web:openskill.studio:orgs:{org_id}"
    credential_id = f"urn:uuid:{snapshot_id}"

    # Build credential subject from snapshot payload
    capabilities = snapshot_payload.get("capabilities", [])
    credential_subject = {
        "id": f"urn:openskill:user:{user_id}",
        "type": "SkillPassportHolder",
        "capabilities": [
            {
                "capabilityId": cap.get("capability_id"),
                "capabilityName": cap.get("capability_name"),
                "level": cap.get("level"),
                "levelLabel": cap.get("level_label"),
                "score": cap.get("score"),
                "confidence": cap.get("confidence"),
                "evidenceCount": cap.get("evidence_count"),
            }
            for cap in capabilities
        ],
    }

    # Build the VC without proof
    vc: dict = {
        "@context": VC_CONTEXT,
        "id": credential_id,
        "type": ["VerifiableCredential", "SkillPassportCredential"],
        "issuer": {
            "id": did,
            "name": org_name or "OpenSkill Studio",
        },
        "issuanceDate": issued_at.isoformat(),
        "credentialSubject": credential_subject,
    }

    if expires_at:
        vc["expirationDate"] = expires_at.isoformat()

    if checksum:
        vc["credentialStatus"] = {
            "type": "IntegrityChecksum",
            "algorithm": "sha-256",
            "value": checksum,
        }

    # Canonicalize for signing (sorted keys, no whitespace)
    canonical = json.dumps(vc, sort_keys=True, separators=(",", ":"))
    signature = sign_payload(canonical, private_key_pem)

    # Add proof
    vc["proof"] = {
        "type": "Ed25519Signature2020",
        "created": datetime.now(UTC).isoformat(),
        "verificationMethod": f"{did}#key-1",
        "proofPurpose": "assertionMethod",
        "proofValue": signature,
    }

    return vc


def verify_vc(vc: dict, public_key_pem: str) -> bool:
    """Verify a W3C VC's Ed25519 proof.

    Returns True if the proof is valid.
    """
    from app.talent.services.credential_signing import verify_signature

    proof = vc.get("proof")
    if not proof or proof.get("type") != "Ed25519Signature2020":
        return False

    signature = proof.get("proofValue")
    if not signature:
        return False

    # Reconstruct the VC without proof for verification
    vc_without_proof = {k: v for k, v in vc.items() if k != "proof"}
    canonical = json.dumps(vc_without_proof, sort_keys=True, separators=(",", ":"))

    return verify_signature(canonical, signature, public_key_pem)
