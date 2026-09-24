"""Dependency graph, impact analysis, telemetry endpoints (Parts G, H, I)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import require_platform_admin
from app.ecosystem.schemas import (
    AddEdgeRequest,
    ComputeImpactRequest,
    EdgeResponse,
    ImpactAnalysisResponse,
    ImpactItemResponse,
    TelemetrySnapshotResponse,
)
from app.ecosystem.services.graph import GraphService
from app.ecosystem.services.impact import ImpactService
from app.ecosystem.services.telemetry import TelemetryService
from app.models.user import User, UserRole
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem — Graph & Impact"])


@router.post("/graph/edges", response_model=DataResponse[EdgeResponse], status_code=201)
async def add_edge(
    body: AddEdgeRequest,
    org_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    edge = await GraphService(db).add_edge(
        from_kind=body.from_kind,
        from_id=body.from_id,
        to_kind=body.to_kind,
        to_id=body.to_id,
        constraint_type=body.constraint_type,
        constraint_spec=body.constraint_spec,
        org_id=org_id if body.org_scoped else None,
    )
    await db.commit()
    return {"data": edge}


@router.delete("/graph/edges/{edge_id}", status_code=204)
async def remove_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    await GraphService(db).remove_edge(edge_id)
    await db.commit()


@router.get("/graph/node/{kind}/{node_id}", response_model=DataResponse[dict])
async def node_edges(
    kind: str,
    node_id: str,
    org_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Cross-tenant guard: an arbitrary org_id would expose that org's PRIVATE
    # dependency edges — membership (or platform admin) is required
    if org_id is not None and user.role != UserRole.ADMIN:
        from app.api.deps import require_org_member

        await require_org_member(org_id, user, db)
    edges = await GraphService(db).edges_for_node(kind, node_id, org_id=org_id)
    return {
        "data": {
            "depends_on": [EdgeResponse.model_validate(e).model_dump() for e in edges["depends_on"]],
            "dependents": [EdgeResponse.model_validate(e).model_dump() for e in edges["dependents"]],
        }
    }


@router.post("/graph/sync-release/{release_id}", response_model=DataResponse[dict])
async def sync_release_edges(
    release_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    created = await GraphService(db).sync_release_edges(release_id)
    await db.commit()
    return {"data": {"edges_created": created}}


# ── Impact analysis ─────────────────────────────────────────────────


@router.post("/impact/analyses", response_model=DataResponse[ImpactAnalysisResponse], status_code=201)
async def compute_impact(
    body: ComputeImpactRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    analysis = await ImpactService(db).compute(body.change_event_id)
    await db.commit()
    return {"data": analysis}


@router.get("/impact/analyses", response_model=DataResponse[list[ImpactAnalysisResponse]])
async def list_impact(
    status: str | None = None,
    classification: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await ImpactService(db).list(
            status=status, classification=classification, limit=limit, offset=offset
        )
    }


@router.get("/impact/analyses/{analysis_id}", response_model=DataResponse[dict])
async def get_impact(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    # Detail view exposes traversal NODES, which can include org-private
    # dependency edges — operator-only; the list view (aggregate counts)
    # stays member-readable
    analysis, items = await ImpactService(db).get(analysis_id)
    return {
        "data": {
            "analysis": ImpactAnalysisResponse.model_validate(analysis).model_dump(),
            "items": [ImpactItemResponse.model_validate(i).model_dump() for i in items],
        }
    }


@router.post("/impact/analyses/{analysis_id}/status", response_model=DataResponse[ImpactAnalysisResponse])
async def set_impact_status(
    analysis_id: str,
    status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    analysis = await ImpactService(db).set_status(analysis_id, status)
    await db.commit()
    return {"data": analysis}


# ── Telemetry (Part G) ──────────────────────────────────────────────


@router.get("/telemetry/snapshots", response_model=DataResponse[list[TelemetrySnapshotResponse]])
async def list_telemetry(
    entity_kind: str | None = None,
    entity_id: str | None = None,
    org_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Org-scoped rows only for platform admins or the org itself; membership
    # is enforced by only honoring org_id for admins here (tenant users read
    # cross-tenant aggregates + must use org-scoped surfaces elsewhere)
    effective_org = org_id if user.role == UserRole.ADMIN else None
    rows = await TelemetryService(db).list_snapshots(
        entity_kind=entity_kind,
        entity_id=entity_id,
        org_id=effective_org,
        limit=limit,
    )
    return {"data": rows}
