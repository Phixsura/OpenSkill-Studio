"""Capability ontology API — CRUD, edges, mappings, traversal.

Authorization:
  - Read (list, get, graph): any authenticated user
  - Write (create, update, merge, edges, mappings): platform admin (UserRole.ADMIN) only
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.base import DataResponse
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
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.services.capability import CapabilityService

router = APIRouter(prefix="/talent/capabilities", tags=["Talent — Capabilities"])


def _require_platform_admin(user: User) -> None:
    """Gate capability ontology mutations to platform admins."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only platform admins can modify the capability ontology")


@router.get("", response_model=CursorListResponse[CapabilityResponse])
async def list_capabilities(
    category: str | None = None,
    status: str = "active",
    parent_id: str | None = Query(None),
    esco_uri: str | None = Query(None, description="Filter by ESCO URI"),
    onet_code: str | None = Query(None, description="Filter by O*NET code"),
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
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
        esco_uri=esco_uri,
        onet_code=onet_code,
        limit=limit,
        cursor=cursor,
    )
    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[CapabilityResponse.model_validate(c) for c in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
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
        external_ids=body.external_ids,
        aliases=body.aliases,
        translations=body.translations,
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


@router.post("/capabilities/resolve", response_model=DataResponse[dict])
async def resolve_skill_names(
    body: dict,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Resolve skill names to canonical capabilities.

    Body: {"names": ["JS", "React.js", "ML"]}
    Returns matches for each name with confidence and match type.
    """
    names = body.get("names", [])
    if not names or not isinstance(names, list):
        raise HTTPException(422, "Request must include a 'names' list")
    if len(names) > 100:
        raise HTTPException(422, "Maximum 100 names per request")

    from app.talent.services.skill_synonyms import SkillSynonymService

    svc = SkillSynonymService(db)
    results = await svc.resolve_batch(names)
    return DataResponse(data=results)


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


# ---- Gap #7: Autocomplete ----

@router.get("/talent/capabilities/autocomplete", response_model=DataResponse[list[dict]])
async def autocomplete_capabilities_endpoint(
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Typeahead autocomplete for capability names."""
    from app.talent.services.skill_intelligence import autocomplete_capabilities
    results = await autocomplete_capabilities(db, q, limit=limit)
    return DataResponse(data=results)


# ---- Gap #8: Skill frequency ----

@router.get("/talent/capabilities/frequency", response_model=DataResponse[list[dict]])
async def get_skill_frequency(
    days: int = Query(90, ge=7, le=365),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Skill usage frequency analytics."""
    from app.talent.services.skill_intelligence import compute_skill_frequency
    results = await compute_skill_frequency(db, days=days, limit=limit)
    return DataResponse(data=results)


# ---- Gap #9: Co-occurrence ----

@router.get("/talent/capabilities/cooccurrence", response_model=DataResponse[list[dict]])
async def get_skill_cooccurrence(
    min_users: int = Query(3, ge=1, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Skill co-occurrence analysis — which skills appear together."""
    from app.talent.services.skill_intelligence import compute_skill_cooccurrence
    results = await compute_skill_cooccurrence(db, min_users=min_users, limit=limit)
    return DataResponse(data=results)


# ---- Gap #2: Taxonomy import ----

@router.post("/talent/capabilities/import", response_model=DataResponse[dict])
async def import_taxonomy(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Bulk import capabilities from ESCO/O*NET/custom format (dry-run validation)."""
    import dataclasses

    from app.talent.services.taxonomy_import import validate_import_batch
    fmt = body.get("format", "custom_json")
    rows = body.get("rows", [])
    result = validate_import_batch(rows, fmt)
    return DataResponse(data=dataclasses.asdict(result))


# ---- Gap #11: Industry taxonomies ----

@router.get("/talent/capabilities/industries", response_model=DataResponse[dict])
async def list_industry_taxonomies(
    user: User = Depends(get_current_user),
):
    """List available industry taxonomy presets."""
    from app.talent.services.taxonomy_import import get_industry_taxonomy, list_available_industries
    industries = list_available_industries()
    return DataResponse(data={
        "industries": industries,
        "presets": {i: get_industry_taxonomy(i) for i in industries},
    })


# ---- Gap #17: API version info ----

@router.get("/talent/capabilities/version", response_model=DataResponse[dict])
async def get_taxonomy_version(
    user: User = Depends(get_current_user),
):
    """Get taxonomy API version and metadata."""
    from app.talent.services.taxonomy_import import TAXONOMY_VERSION_INFO
    return DataResponse(data=TAXONOMY_VERSION_INFO)


# ---- Gap #15: Edge strength ----

@router.get("/talent/capabilities/edge-strength", response_model=DataResponse[dict])
async def get_edge_strength(
    source_id: str = Query(...),
    target_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compute relationship strength between two capabilities."""
    from app.talent.services.skill_intelligence import compute_edge_strength
    strength = await compute_edge_strength(db, source_id, target_id)
    return DataResponse(data={"source_id": source_id, "target_id": target_id, "strength": strength})


# ---- Gap #72: Search analytics ----

@router.get("/talent/capabilities/search-analytics", response_model=DataResponse[dict])
async def get_search_analytics_endpoint(
    user: User = Depends(get_current_user),
):
    """Search analytics — popular queries, zero-result tracking."""
    from app.talent.services.search_intelligence import get_search_analytics
    store = get_search_analytics()
    return DataResponse(data={
        "stats": store.get_stats(),
        "popular": store.get_popular_queries(20),
        "zero_results": store.get_zero_result_queries(20),
    })


# ---- Gap #79: Boolean search ----

@router.post("/talent/capabilities/boolean-search", response_model=DataResponse[dict])
async def boolean_search(
    body: dict,
    user: User = Depends(get_current_user),
):
    """Parse a Boolean search query into structured form."""
    from app.talent.services.search_intelligence import parse_boolean_query
    parsed = parse_boolean_query(body.get("query", ""))
    return DataResponse(data=parsed)


# ---- Gap #75: Match feedback ----

@router.post("/talent/match-feedback", response_model=DataResponse[dict])
async def submit_match_feedback(
    body: dict,
    user: User = Depends(get_current_user),
):
    """Submit feedback on match quality."""
    from app.talent.services.search_intelligence import validate_match_feedback
    errors = validate_match_feedback(body.get("rating", ""))
    if errors:
        raise HTTPException(422, errors[0])
    return DataResponse(data={"submitted": True, "rating": body["rating"]})
