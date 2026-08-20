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

    model_config = {"from_attributes": True}


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
