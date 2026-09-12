"""Certificate verification endpoint — public, no auth required."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.certificate import Certificate
from app.schemas.base import DataResponse

router = APIRouter(tags=["Certificates"])


class CertificateResponse(BaseModel):
    id: str
    certificate_number: str
    issued_at: datetime
    data: dict
    # Flattened fields from data dict for frontend convenience
    user_name: str | None = None
    path_name: str | None = None
    org_name: str | None = None
    skills_completed: int | None = None
    # R113[M6]: white-label footer (tenant branding), verification view only
    certificate_footer: str | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _flatten_data(self) -> "CertificateResponse":
        # R90c: the endpoint builds this via model_validate(orm_obj), which does
        # NOT call __init__ — so the previous __init__-based flattening silently
        # left user_name/path_name/org_name/skills_completed as None for every
        # verified certificate (the public page reads these top-level fields).
        # A model_validator(after) runs on BOTH model_validate and direct
        # construction, so the flattening always applies.
        data = self.data or {}
        if self.user_name is None:
            self.user_name = data.get("user_name")
        if self.path_name is None:
            self.path_name = data.get("path_name")
        if self.org_name is None:
            self.org_name = data.get("org_name")
        if self.skills_completed is None:
            self.skills_completed = data.get("skills_completed")
        return self


@router.get(
    "/certificates/{certificate_number}",
    response_model=DataResponse[CertificateResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def verify_certificate(
    certificate_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Public certificate verification — no authentication required."""
    # R88: this anon endpoint takes a user-controlled path param straight into
    # a parameterized query. A NUL byte (%00) in the value is a valid str after
    # URL-decoding but crashes the asyncpg bind with 22P05
    # (CharacterNotInRepertoireError, a DBAPIError not ValueError) → unhandled
    # 500. A NUL can never match a real certificate_number, so treat it (and any
    # control char) as a clean not-found rather than letting it reach the DB.
    if "\x00" in certificate_number or any(ord(ch) < 32 for ch in certificate_number):
        raise AppError("CERTIFICATE_NOT_FOUND", "Certificate not found", 404)
    result = await db.execute(
        select(Certificate).where(Certificate.certificate_number == certificate_number)
    )
    cert = result.scalar_one_or_none()
    if cert is None:
        raise AppError("CERTIFICATE_NOT_FOUND", "Certificate not found", 404)
    response = CertificateResponse.model_validate(cert)
    # R113[M6]: certificate_footer was validated, stored and UI-editable but
    # nothing ever read it — wire the tenant's white-label footer into the
    # public verification view (the only certificate rendering surface).
    try:
        from app.controlplane.models.branding import TenantBranding
        from app.models.organization import Organization

        tenant_id = (
            await db.execute(select(Organization.tenant_id).where(Organization.id == cert.org_id))
        ).scalar_one_or_none()
        if tenant_id:
            footer = (
                await db.execute(
                    select(TenantBranding.certificate_footer).where(
                        TenantBranding.tenant_id == tenant_id
                    )
                )
            ).scalar_one_or_none()
            if footer:
                response.certificate_footer = footer
    except Exception:  # noqa: BLE001 — branding is cosmetic; never fail verification
        pass
    return DataResponse(data=response)
