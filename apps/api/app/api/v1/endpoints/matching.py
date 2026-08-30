"""Matching endpoints (ADR-012) — audited, explainable recommendations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.matching import FeedbackEvent, MatchResult, MatchRun
from app.models.organization import OrgRole
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

_WRITE_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


async def _resolve_names(
    db: AsyncSession, entity_type: str, entity_ids: list[str], org_id: str
) -> dict:
    """Resolve entity_id → name, but ONLY for entities the requesting org can
    CURRENTLY see (R86). MatchResult rows persist entity_id only (no name
    snapshot), so names are re-resolved live on every historical read. A
    foreign pack legitimately captured in a run while it was PUBLIC+approved
    can later be renamed (which voids approval → UNLISTED), archived, or made
    private — a bare `SELECT name WHERE id IN (...)` would then leak the pack's
    CURRENT (possibly secret) name and continued existence to an org that can
    no longer see it. Mirror the S1 eligibility rule (candidates.py): own-org
    packs (any visibility) OR public+published+approved; anything else resolves
    to None (rendered as a redacted row, not a name leak)."""
    if not entity_ids:
        return {}
    if entity_type in ("workflow_pack", "skill_pack"):
        from app.models.skill_pack import PackStatus, PackVisibility

        model = WorkflowPack if entity_type == "workflow_pack" else SkillPack
        visible = or_(
            model.owner_org_id == org_id,
            (model.visibility == PackVisibility.PUBLIC)
            & (model.status == PackStatus.PUBLISHED)
            & (or_(model.review_status.is_(None), model.review_status == "approved")),
        )
        rows = await db.execute(
            select(model.id, model.name).where(model.id.in_(entity_ids), visible)
        )
    elif entity_type == "project_template":
        # Templates are org-scoped — only this org's templates were ever
        # eligible; still filter defensively so a stale foreign id can't leak.
        rows = await db.execute(
            select(ProjectTemplate.id, ProjectTemplate.name).where(
                ProjectTemplate.id.in_(entity_ids),
                ProjectTemplate.org_id == org_id,
            )
        )
    elif entity_type == "creator":
        # Creators are ranked from the org's own ACTIVE members — resolve only
        # names of users who are currently active members of THIS org, so a
        # user who has since left does not leak their display_name.
        from app.models.organization import MemberStatus, OrgMember

        rows = await db.execute(
            select(User.id, User.display_name)
            .join(OrgMember, OrgMember.user_id == User.id)
            .where(
                User.id.in_(entity_ids),
                OrgMember.org_id == org_id,
                OrgMember.status == MemberStatus.ACTIVE,
            )
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
    # Creator matching ranks PEOPLE (scores, evidence gaps, exclusion
    # reasons) — instructor+ only, same gate as the shortlist endpoint.
    # Leaving it member-open lets any student run talent rankings over
    # the whole org through this generic surface.
    if body.target_entity_type == "creator":
        member = await require_org_member(org_id, user, db, *_WRITE_ROLES)
    else:
        member = await require_org_member(org_id, user, db)
    profile_svc = RequirementProfileService(db)
    # R89e: a requirement profile carries a confidential raw_request/brief. The
    # GET/list profile routes hide a peer's profile from non-instructors
    # (only_user_id), but run_match fetched it with only_user_id=None — so a
    # student who guessed/enumerated a profile id could run a match against an
    # instructor's confidential profile (and read its derived constraints in the
    # explain tree) through this side door. Apply the same owner gate here.
    only_user_id = None if member.role in _WRITE_ROLES else user.id
    profile = await profile_svc.get_profile(
        body.requirement_profile_id, org_id, only_user_id=only_user_id
    )
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
        db, body.target_entity_type, [r.entity_id for r in results], org_id
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
    member = await require_org_member(org_id, user, db)
    # R89e: a match run references a requirement profile whose constraints are
    # confidential to its owner. Instructors+ see all org runs (moderation);
    # a non-instructor sees only their own — otherwise the history list is a
    # side door to peers'/instructors' runs (and their creator rankings).
    own_only = member.role not in _WRITE_ROLES
    base_filter = [MatchRun.org_id == org_id]
    if own_only:
        base_filter.append(MatchRun.created_by == user.id)
    total_r = await db.execute(
        select(func.count()).select_from(MatchRun).where(*base_filter)
    )
    total = total_r.scalar_one()
    result = await db.execute(
        select(MatchRun)
        .where(*base_filter)
        .order_by(MatchRun.created_at.desc(), MatchRun.id.desc())
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
    member = await require_org_member(org_id, user, db)
    run = await db.get(MatchRun, run_id)
    if run is None or run.org_id != org_id:
        raise AppError("MATCH_RUN_NOT_FOUND", "Match run not found", 404)
    # R89e: a persisted run holds a full ranking derived from a confidential
    # requirement profile (and, for creator runs, people scores + exclusion
    # reasons). Reading history must not be a side door around the profile's
    # owner gate. Instructors+ may read any org run (moderation); a
    # non-instructor may read only their own. Uniform 404 (not 403) keeps run
    # ids non-enumerable. (Previously only creator runs were gated, so a
    # student could read any workflow_pack/skill_pack/template run in the org.)
    if member.role not in _WRITE_ROLES and run.created_by != user.id:
        raise AppError("MATCH_RUN_NOT_FOUND", "Match run not found", 404)
    results_r = await db.execute(
        select(MatchResult).where(MatchResult.match_run_id == run_id)
    )
    results = list(results_r.scalars().all())
    names = await _resolve_names(
        db, run.target_entity_type, [r.entity_id for r in results], org_id
    )
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
