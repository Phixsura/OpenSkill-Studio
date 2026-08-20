"""LTI 1.3 Integration — coming soon placeholder."""

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit
from app.schemas.base import DataResponse

router = APIRouter(tags=["LTI"])


@router.get(
    "/lti/config/{pack_id}",
    response_model=DataResponse[dict],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_lti_config(pack_id: str):
    """Return LTI 1.3 integration status for a pack."""
    return DataResponse(
        data={
            "pack_id": pack_id,
            "status": "coming_soon",
            "note": "LTI 1.3 integration is planned for a future release",
        }
    )
