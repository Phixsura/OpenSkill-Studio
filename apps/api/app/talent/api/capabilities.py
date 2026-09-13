"""Capability ontology API — CRUD, edges, mappings, traversal.

Authorization:
  - Read (list, get, graph): any authenticated user
  - Write (create, update, merge, edges, mappings): platform admin (UserRole.ADMIN) only
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.schemas.capability import (
    CapabilityResponse,
    CreateCapabilityRequest,
    CreateEdgeRequest,
    CreateMappingRequest,
    EdgeResponse,
    GraphResponse,
    MappingResponse,
    MergeCapabilityRequest,
    UpdateCapabilityRequest,
)
from app.talent.services.capability import CapabilityService

router = APIRouter(prefix="/talent/capabilities", tags=["Talent — Capabilities"])


def _require_platform_admin(user: User) -> None:
    """Gate capability ontology mutations to platform admins."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only platform admins can modify the capability ontology")


@router.get("", response_model=ListResponse[CapabilityResponse])
async def list_capabilities(
    category: str | None = None,
    status: str = "active",
    parent_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityService(db)
    # Use ... sentinel for "no filter" vs None for "root only"
    pid = ... if parent_id is None else (None if parent_id == "root" else parent_id)
    items, total = await svc.list_capabilities(
        category=category,
        status=status,
        parent_id=pid,
        limit=per_page,
        offset=(page - 1) * per_page,
    )
    return ListResponse(
        data=[CapabilityResponse.model_validate(c) for c in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.post("", response_model=DataResponse[CapabilityResponse], status_code=201)
async def create_capability(
    body: CreateCapabilityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_platform_admin(user)
    svc = CapabilityService(db)
    cap = await svc.create_capability(
        canonical_name=body.canonical_name,
        category=body.category,
        description=body.description,
        parent_id=body.parent_id,
        capability_tag_id=body.capability_tag_id,
        level_definitions=body.level_definitions,
        decay_config=body.decay_config,
        sort_order=body.sort_order,
    )
    await db.commit()
    await db.refresh(cap)
    return DataResponse(data=CapabilityResponse.model_validate(cap))


@router.get("/{capability_id}", response_model=DataResponse[CapabilityResponse])
async def get_capability(
    capability_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityService(db)
    cap = await svc.get_capability(capability_id)
    if not cap:
        raise HTTPException(404, "Capability not found")
    return DataResponse(data=CapabilityResponse.model_validate(cap))


@router.patch("/{capability_id}", response_model=DataResponse[CapabilityResponse])
async def update_capability(
    capability_id: str,
    body: UpdateCapabilityRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    fields = body.model_dump(exclude_unset=True)
    cap = await svc.update_capability(capability_id, **fields)
    if not cap:
        raise HTTPException(404, "Capability not found")
    await db.commit()
    await db.refresh(cap)
    return DataResponse(data=CapabilityResponse.model_validate(cap))


@router.post("/{capability_id}/merge", response_model=DataResponse[CapabilityResponse])
async def merge_capability(
    capability_id: str,
    body: MergeCapabilityRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    try:
        cap = await svc.merge_capability(capability_id, body.target_id)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not cap:
        raise HTTPException(404, "Capability not found")
    await db.commit()
    await db.refresh(cap)
    return DataResponse(data=CapabilityResponse.model_validate(cap))


# ---- Edges ----

@router.post("/{capability_id}/edges", response_model=DataResponse[EdgeResponse], status_code=201)
async def add_edge(
    capability_id: str,
    body: CreateEdgeRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    # Ensure source matches the URL
    if body.source_id != capability_id:
        body.source_id = capability_id
    try:
        edge = await svc.add_edge(
            source_id=body.source_id,
            target_id=body.target_id,
            edge_type=body.edge_type,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    await db.refresh(edge)
    return DataResponse(data=EdgeResponse.model_validate(edge))


@router.delete("/{capability_id}/edges/{edge_id}", status_code=204)
async def remove_edge(
    capability_id: str,
    edge_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    if not await svc.remove_edge(edge_id):
        raise HTTPException(404, "Edge not found")
    await db.commit()


@router.get("/{capability_id}/edges", response_model=DataResponse[list[EdgeResponse]])
async def get_edges(
    capability_id: str,
    direction: str = Query("both", pattern="^(outgoing|incoming|both)$"),
    edge_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityService(db)
    edges = await svc.get_edges(capability_id, direction=direction, edge_type=edge_type)
    return DataResponse(data=[EdgeResponse.model_validate(e) for e in edges])


# ---- Graph traversal ----

@router.get("/{capability_id}/graph", response_model=DataResponse[GraphResponse])
async def traverse_graph(
    capability_id: str,
    max_depth: int = Query(3, ge=1, le=20),
    edge_types: str | None = Query(None, description="Comma-separated edge types"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityService(db)
    types = set(edge_types.split(",")) if edge_types else None
    graph = await svc.traverse_graph(capability_id, edge_types=types, max_depth=max_depth)
    if not graph:
        raise HTTPException(404, "Capability not found")
    return DataResponse(data=GraphResponse(**graph))


# ---- Mappings ----

@router.post("/mappings", response_model=DataResponse[MappingResponse], status_code=201)
async def create_mapping(
    body: CreateMappingRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    try:
        mapping = await svc.create_mapping(
            capability_id=body.capability_id,
            source_type=body.source_type,
            source_id=body.source_id,
            contribution_weight=body.contribution_weight,
            evidence_type=body.evidence_type,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    await db.refresh(mapping)
    return DataResponse(data=MappingResponse.model_validate(mapping))


@router.get("/mappings", response_model=DataResponse[list[MappingResponse]])
async def list_mappings(
    capability_id: str | None = None,
    source_type: str | None = None,
    source_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    svc = CapabilityService(db)
    mappings = await svc.get_mappings(
        capability_id=capability_id,
        source_type=source_type,
        source_id=source_id,
    )
    return DataResponse(data=[MappingResponse.model_validate(m) for m in mappings])


@router.delete("/mappings/{mapping_id}", status_code=204)
async def delete_mapping(
    mapping_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    _require_platform_admin(_user)
    svc = CapabilityService(db)
    if not await svc.delete_mapping(mapping_id):
        raise HTTPException(404, "Mapping not found")
    await db.commit()
