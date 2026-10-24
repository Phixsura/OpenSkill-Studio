"""Manifest validation endpoint — mirrors CLI validation on server side."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse
from app.services.manifest_validator import validate_manifest

router = APIRouter(tags=["Manifest Validation"])


class ValidateManifestRequest(BaseModel):
    manifest: dict


@router.post(
    "/developer/validate-manifest",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def validate_app_manifest(
    body: ValidateManifestRequest,
    user: User = Depends(get_current_user),
):
    """Validate an app manifest against the platform schema.

    Returns validation result with errors and warnings.
    This endpoint mirrors the CLI's `openskill validate` command.
    """
    result = validate_manifest(body.manifest)
    return DataResponse(data=result.to_dict())
