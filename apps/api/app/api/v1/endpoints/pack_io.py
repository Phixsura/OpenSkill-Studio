"""Pack import/export endpoints."""

import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.skill_pack import ReleaseResponse, SkillPackResponse
from app.services.pack_export import PackExportService
from app.services.pack_import import MAX_ARCHIVE_SIZE, PackImportService

router = APIRouter(tags=["Pack Import/Export"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.get("/orgs/{org_id}/packs/{pack_id}/releases/{version}/export", dependencies=[Depends(rate_limit(10, 60))])
async def export_release(
    org_id: str,
    pack_id: str,
    version: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export a release as a downloadable zip archive."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    # Verify pack ownership
    from app.services.skill_pack import SkillPackService

    await SkillPackService(db).get_pack(pack_id, org_id)

    svc = PackExportService(db)
    zip_bytes, filename = await svc.export_release(pack_id, version)
    # Sanitize filename for Content-Disposition header
    import re
    safe_filename = re.sub(r'[^\w\-.]', '_', filename)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )


@router.post(
    "/orgs/{org_id}/packs/import",
    response_model=DataResponse[dict],
    status_code=201,
    dependencies=[Depends(rate_limit(3, 60))],
)
async def import_pack(
    org_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import a pack from a zip archive."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)

    # Read upload in bounded chunks to prevent OOM from unbounded reads
    buf = io.BytesIO()
    chunk_size = 1024 * 1024  # 1 MB chunks
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        buf.write(chunk)
        if buf.tell() > MAX_ARCHIVE_SIZE:
            raise AppError(
                "FILE_TOO_LARGE",
                f"Upload exceeds {MAX_ARCHIVE_SIZE // (1024 * 1024)}MB limit",
                413,
            )
    file_bytes = buf.getvalue()
    svc = PackImportService(db)
    pack, release = await svc.import_pack(org_id, file_bytes, user.id)
    await db.commit()
    return DataResponse(data={
        "pack": SkillPackResponse.model_validate(pack).model_dump(),
        "release": ReleaseResponse.model_validate(release).model_dump(),
    })
