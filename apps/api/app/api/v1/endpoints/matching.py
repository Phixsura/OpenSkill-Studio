"""Matching endpoints (ADR-012) — audited, explainable recommendations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.matching import FeedbackEvent, MatchResult, MatchRun
from app.models.project import ProjectTemplate
from app.models.skill_pack import SkillPack
from app.models.user import User
from app.models.workflow_pack import WorkflowPack
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.matching import (
    ExcludedItem,
    FeedbackEventRequest,
    MatchRequest,
    MatchResultItem,
    MatchRunResponse,
)
from app.services.matching import MatchingEngine, MatchSpec
from app.services.requirement_profile import RequirementProfileService

router = APIRouter(tags=["Matching"])


async def _resolve_names(db: AsyncSession, entity_type: str, entity_ids: list[str]) -> dict:
    if not entity_ids:
        return {}
    if entity_type == "workflow_pack":
        rows = await db.execute(
            select(WorkflowPack.id, WorkflowPack.name).where(WorkflowPack.id.in_(entity_ids))
        )
    elif entity_type == "skill_pack":
        rows = await db.execute(
            select(SkillPack.id, SkillPack.name).where(SkillPack.id.in_(entity_ids))
        )
    elif entity_type == "project_template":
        rows = await db.execute(
            select(ProjectTemplate.id, ProjectTemplate.name).where(
                ProjectTemplate.id.in_(entity_ids)
            )
        )
    elif entity_type == "creator":
        rows = await db.execute(
            select(User.id, User.display_name).where(User.id.in_(entity_ids))
        )
    else:
        return {}
    return {row[0]: row[1] for row in rows.all()}


def _build_run_response(
    run: MatchRun,
    results: list[MatchResult],
    names: dict,
    explain_trees: list[dict] | None = None,
) -> MatchRunResponse:
    ranked = sorted(
        (r for r in results if r.rank is not None), key=lambda r: r.rank
    )
    excluded = [r for r in results if r.rank is None]
    items = []
    for i, r in enumerate(ranked):
        items.append(
            MatchResultItem(
                entity_id=r.entity_id,
                entity_type=r.entity_type,
                name=names.get(r.entity_id),
                rank=r.rank,
                score=float(r.score) if r.score is not None else None,
                tier=r.tier,
                reasons=r.reasons,
                gaps=r.gaps,
                explain=(explain_trees[i] if explain_trees and i < len(explain_trees) else None),
            )
        )
    return MatchRunResponse(
        id=run.id,
        org_id=run.org_id,
        target_entity_type=run.target_entity_type,
        engine_version=run.engine_version,
        config_version=run.config_version,
        candidate_count=run.candidate_count,
        excluded_count=run.excluded_count,
        created_at=run.created_at,
        results=items,
        excluded=[
            ExcludedItem(
                entity_id=r.entity_id,
                name=names.get(r.entity_id),
                failures=r.hard_failures,
            )
            for r in excluded
        ],
    )


@router.post(
    "/orgs/{org_id}/match",
    response_model=DataResponse[MatchRunResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def run_match(
    org_id: str,
    body: MatchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    profile_svc = RequirementProfileService(db)
    profile = await profile_svc.get_profile(body.requirement_profile_id, org_id)
    if profile.status != "confirmed":
        raise AppError(
            "PROFILE_NOT_CONFIRMED",
            "The requirement profile must be confirmed before matching",
            422,
        )

    # R14: extracted-only values never enter hard constraints
    requirement = profile_svc.build_match_requirement(profile)

    engine = MatchingEngine(db)
    run, results, explain_trees = await engine.run(
        MatchSpec(
            org_id=org_id,
            target_entity_type=body.target_entity_type,
            requirement=requirement,
            context_type=profile.context_type.value,
            requirement_profile_id=profile.id,
            created_by=user.id,
            limit=body.limit,
            explain=body.explain,
        )
    )
    await db.commit()

    names = await _resolve_names(
        db, body.target_entity_type, [r.entity_id for r in results]
    )
    return DataResponse(
        data=_build_run_response(run, results, names, explain_trees if body.explain else None)
    )


@router.get(
    "/orgs/{org_id}/match-runs",
    response_model=ListResponse[MatchRunResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_match_runs(
    org_id: str,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    total_r = await db.execute(
        select(func.count()).select_from(MatchRun).where(MatchRun.org_id == org_id)
    )
    total = total_r.scalar_one()
    result = await db.execute(
        select(MatchRun)
        .where(MatchRun.org_id == org_id)
        .order_by(MatchRun.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    runs = list(result.scalars().all())
    responses = []
    for run in runs:
        responses.append(
            MatchRunResponse(
                id=run.id,
                org_id=run.org_id,
                target_entity_type=run.target_entity_type,
                engine_version=run.engine_version,
                config_version=run.config_version,
                candidate_count=run.candidate_count,
                excluded_count=run.excluded_count,
                created_at=run.created_at,
            )
        )
    return ListResponse(
        data=responses,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/match-runs/{run_id}",
    response_model=DataResponse[MatchRunResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_match_run(
    org_id: str,
    run_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    run = await db.get(MatchRun, run_id)
    if run is None or run.org_id != org_id:
        raise AppError("MATCH_RUN_NOT_FOUND", "Match run not found", 404)
    results_r = await db.execute(
        select(MatchResult).where(MatchResult.match_run_id == run_id)
    )
    results = list(results_r.scalars().all())
    names = await _resolve_names(db, run.target_entity_type, [r.entity_id for r in results])
    return DataResponse(data=_build_run_response(run, results, names))


@router.post(
    "/orgs/{org_id}/feedback-events",
    status_code=201,
    dependencies=[Depends(rate_limit(60, 60))],
)
async def record_feedback(
    org_id: str,
    body: FeedbackEventRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    # match_run_id is a loose (non-FK) reference — verify org ownership so
    # feedback rows cannot be attached to another org's match runs.
    if body.match_run_id is not None:
        run = await db.get(MatchRun, body.match_run_id)
        if run is None or run.org_id != org_id:
            raise AppError("MATCH_RUN_NOT_FOUND", "Match run not found", 404)
    event = FeedbackEvent(
        org_id=org_id,
        match_run_id=body.match_run_id,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        event_type=body.event_type,
        rank_position=body.rank_position,
        created_by=user.id,
    )
    db.add(event)
    await db.commit()
    return {"data": {"id": event.id}}
