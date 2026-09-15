"""Open Badges 3.0 credential export (ADR-015 D-VC).

Implements:
  - 1EdTech Open Badges 3.0 (https://1edtech.github.io/openbadges-specification/ob_v3p0.html)
  - OpenBadgeCredential / AchievementCredential types
  - ESCO/O*NET alignment via Capability.external_ids
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from app.talent.services.credential_signing import sign_payload

# Open Badges 3.0 context
OB3_CONTEXT = [
    "https://www.w3.org/2018/credentials/v1",
    "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json",
]


def export_credential_as_ob3(
    *,
    credential_id: str,
    credential_type: str,
    user_id: str,
    issued_at: datetime,
    expires_at: datetime | None,
    capabilities: list[dict],
    org_id: str,
    org_name: str | None = None,
    signing_key_id: str,
    private_key_pem: str,
    capability_details: list[dict] | None = None,
) -> dict:
    """Export a credential as an Open Badges 3.0 OpenBadgeCredential.

    Args:
        credential_id: ULID of the Credential record
        credential_type: e.g. "python_fundamentals"
        user_id: recipient user ID
        issued_at: credential issuance datetime
        expires_at: optional expiration
        capabilities: list of {capability_id, required_level, achieved_level}
        org_id: issuer organization ID
        org_name: issuer display name
        signing_key_id: OrgSigningKey ID for proof
        private_key_pem: PEM-encoded Ed25519 private key
        capability_details: enriched capability data with names, external_ids, descriptions
    """
    did = f"did:web:openskill.studio:orgs:{org_id}"
    cap_details_map = {}
    if capability_details:
        cap_details_map = {c["id"]: c for c in capability_details}

    # Build alignment entries from capability external IDs
    alignment = []
    for cap in capabilities:
        cap_id = cap.get("capability_id")
        detail = cap_details_map.get(cap_id, {})
        external_ids = detail.get("external_ids", {})

        if external_ids.get("esco_uri"):
            alignment.append({
                "type": ["Alignment"],
                "targetUrl": external_ids["esco_uri"],
                "targetName": detail.get("canonical_name", cap_id),
                "targetDescription": f"ESCO skill: {detail.get('canonical_name', '')}",
                "targetFramework": "ESCO",
            })

        if external_ids.get("onet_code"):
            alignment.append({
                "type": ["Alignment"],
                "targetUrl": f"https://www.onetonline.org/link/summary/{external_ids['onet_code']}",
                "targetName": detail.get("canonical_name", cap_id),
                "targetDescription": f"O*NET element: {external_ids['onet_code']}",
                "targetFramework": "O*NET",
            })

    # Build the achievement
    achievement = {
        "id": f"urn:openskill:achievement:{credential_type}",
        "type": ["Achievement"],
        "name": credential_type.replace("_", " ").title(),
        "description": f"Verified competency in {credential_type.replace('_', ' ')}",
        "criteria": {
            "narrative": _build_criteria_narrative(capabilities, cap_details_map),
        },
    }

    if alignment:
        achievement["alignment"] = alignment

    # Build the OB3 credential
    ob3: dict = {
        "@context": OB3_CONTEXT,
        "id": f"urn:uuid:{credential_id}",
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "issuer": {
            "id": did,
            "type": ["Profile"],
            "name": org_name or "OpenSkill Studio",
        },
        "issuanceDate": issued_at.isoformat(),
        "name": achievement["name"],
        "credentialSubject": {
            "id": f"urn:openskill:user:{user_id}",
            "type": ["AchievementSubject"],
            "achievement": achievement,
        },
    }

    if expires_at:
        ob3["expirationDate"] = expires_at.isoformat()

    # Sign
    canonical = json.dumps(ob3, sort_keys=True, separators=(",", ":"))
    signature = sign_payload(canonical, private_key_pem)

    ob3["proof"] = {
        "type": "Ed25519Signature2020",
        "created": datetime.now(UTC).isoformat(),
        "verificationMethod": f"{did}#key-1",
        "proofPurpose": "assertionMethod",
        "proofValue": signature,
    }

    return ob3


def verify_ob3(ob3: dict, public_key_pem: str) -> bool:
    """Verify an OB3 credential's Ed25519 proof."""
    from app.talent.services.credential_signing import verify_signature

    proof = ob3.get("proof")
    if not proof or proof.get("type") != "Ed25519Signature2020":
        return False

    signature = proof.get("proofValue")
    if not signature:
        return False

    ob3_without_proof = {k: v for k, v in ob3.items() if k != "proof"}
    canonical = json.dumps(ob3_without_proof, sort_keys=True, separators=(",", ":"))
    return verify_signature(canonical, signature, public_key_pem)


def _build_criteria_narrative(
    capabilities: list[dict], details_map: dict
) -> str:
    """Build a human-readable criteria narrative for the achievement."""
    if not capabilities:
        return "Credential awarded based on verified assessment."

    lines = ["To earn this credential, the recipient demonstrated:"]
    for cap in capabilities:
        cap_id = cap.get("capability_id", "unknown")
        detail = details_map.get(cap_id, {})
        name = detail.get("canonical_name", cap_id)
        required = cap.get("required_level", 0)
        achieved = cap.get("achieved_level", 0)
        lines.append(
            f"- {name}: achieved level {achieved} (required: {required})"
        )

    return "\n".join(lines)
