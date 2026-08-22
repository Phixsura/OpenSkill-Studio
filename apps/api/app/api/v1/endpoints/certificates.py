"""Certificate verification endpoint — public, no auth required."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
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

    model_config = {"from_attributes": True}

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        # Spread data dict fields to top level
        data = self.data or {}
        if self.user_name is None:
            self.user_name = data.get("user_name")
        if self.path_name is None:
            self.path_name = data.get("path_name")
        if self.org_name is None:
            self.org_name = data.get("org_name")
        if self.skills_completed is None:
            self.skills_completed = data.get("skills_completed")


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
    result = await db.execute(
        select(Certificate).where(Certificate.certificate_number == certificate_number)
    )
    cert = result.scalar_one_or_none()
    if cert is None:
        raise AppError("CERTIFICATE_NOT_FOUND", "Certificate not found", 404)
    return DataResponse(data=CertificateResponse.model_validate(cert))
