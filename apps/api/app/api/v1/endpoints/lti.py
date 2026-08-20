"""LTI 1.3 Basic Integration — stub configuration endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.skill_pack import SkillPack
from app.schemas.base import DataResponse

router = APIRouter(tags=["LTI"])


@router.get(
    "/lti/config/{pack_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_lti_config(
    pack_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return LTI 1.3 configuration JSON for a pack (stub for LMS registration)."""
    pack = await db.get(SkillPack, pack_id)
    if (
        pack is None
        or pack.visibility != PackVisibility.PUBLIC
        or pack.status != PackStatus.PUBLISHED
    ):
        raise AppError("PACK_NOT_FOUND", "Pack not found", 404)

    config = {
        "title": pack.name,
        "description": pack.summary or "",
        "target_link_uri": f"https://app.openskill.studio/lti/launch/{pack_id}",
        "oidc_initiation_url": "https://app.openskill.studio/lti/login",
        "public_jwk_url": "https://app.openskill.studio/lti/jwks",
    }
    return DataResponse(data=config)
