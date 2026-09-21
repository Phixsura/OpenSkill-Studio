"""DID:web document endpoint for organization verification keys."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.base import DataResponse
from app.talent.services.credential_signing import (
    SigningKeyService,
    build_did_document,
)

router = APIRouter(tags=["Talent — DID"])


@router.get(
    "/talent/orgs/{org_id}/did.json",
    response_model=DataResponse[dict],
    summary="Get Did Document",
)
async def get_did_document(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — returns the DID:web document for an organization.

    Contains the organization's Ed25519 public key for verifying
    W3C Verifiable Credentials and Open Badges 3.0 credentials.
    No authentication required — public keys are public.
    """
    key_svc = SigningKeyService(db)
    signing_key = await key_svc.get_active_key_for_org(org_id)
    if not signing_key:
        raise HTTPException(404, "No signing key found for this organization")

    did_doc = build_did_document(org_id, signing_key.public_key)
    return JSONResponse(content=did_doc, media_type="application/did+ld+json")
