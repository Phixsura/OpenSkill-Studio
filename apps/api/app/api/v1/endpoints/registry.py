"""Public registry endpoints — no auth required for public packs."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.skill_pack import ReleaseResponse, SkillPackResponse
from app.services.registry import RegistryService

router = APIRouter(tags=["Registry"])


@router.get("/registry/packs", response_model=ListResponse[SkillPackResponse])
async def search_registry(
    search: str | None = None,
    scenario: str | None = None,
    tool: str | None = None,
    difficulty: str | None = None,
    sort: str = "newest",
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search public skill packs. No authentication required."""
    svc = RegistryService(db)
    packs, total = await svc.search_packs(search, scenario, tool, difficulty, sort, page, per_page)
    return ListResponse(
        data=[SkillPackResponse.model_validate(p) for p in packs],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get("/registry/packs/{pack_id}", response_model=DataResponse[SkillPackResponse])
async def get_registry_pack(pack_id: str, db: AsyncSession = Depends(get_db)):
    """Get a public/unlisted pack detail."""
    svc = RegistryService(db)
    pack = await svc.get_public_pack(pack_id)
    return DataResponse(data=SkillPackResponse.model_validate(pack))


@router.get("/registry/packs/{pack_id}/releases", response_model=DataResponse[list[ReleaseResponse]])
async def get_registry_releases(pack_id: str, db: AsyncSession = Depends(get_db)):
    """List releases for a public pack."""
    svc = RegistryService(db)
    releases = await svc.get_public_releases(pack_id)
    return DataResponse(data=[ReleaseResponse.model_validate(r) for r in releases])
