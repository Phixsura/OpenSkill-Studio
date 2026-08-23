"""S1 — eligibility / candidate generation (silent exclusions).

Ineligible entities never appear ANYWHERE in match output — not even in the
excluded list. Cross-org private content is invisible, not "excluded".
"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import MemberStatus, OrgMember
from app.models.project import ProjectTemplate
from app.models.skill import ContentStatus
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack
from app.models.user import User, UserStatus
from app.models.workflow_pack import WorkflowPack


def _pack_eligibility_filter(model, org_id: str):
    """Public+published+approved packs, plus the org's own packs."""
    return or_(
        # Public registry rules
        (model.visibility == PackVisibility.PUBLIC)
        & (model.status == PackStatus.PUBLISHED)
        & (or_(model.review_status.is_(None), model.review_status == "approved")),
        # Own org's packs (any visibility, not archived)
        (model.owner_org_id == org_id) & (model.status != PackStatus.ARCHIVED),
    )


async def get_candidates(db: AsyncSession, spec) -> list:
    """Return eligible candidates for the spec's target entity type."""
    if spec.target_entity_type == "workflow_pack":
        result = await db.execute(
            select(WorkflowPack).where(
                _pack_eligibility_filter(WorkflowPack, spec.org_id),
                WorkflowPack.status != PackStatus.ARCHIVED,
            )
        )
        return list(result.scalars().all())

    if spec.target_entity_type == "skill_pack":
        result = await db.execute(
            select(SkillPack).where(
                _pack_eligibility_filter(SkillPack, spec.org_id),
                SkillPack.status != PackStatus.ARCHIVED,
            )
        )
        return list(result.scalars().all())

    if spec.target_entity_type == "project_template":
        result = await db.execute(
            select(ProjectTemplate).where(
                ProjectTemplate.org_id == spec.org_id,
                ProjectTemplate.status != ContentStatus.ARCHIVED,
            )
        )
        return list(result.scalars().all())

    if spec.target_entity_type == "creator":
        # R9: read ONLY id / display_name / last_login_at — protected
        # attributes are structurally absent from the feature set.
        result = await db.execute(
            select(User.id, User.display_name, User.last_login_at)
            .join(OrgMember, OrgMember.user_id == User.id)
            .where(
                OrgMember.org_id == spec.org_id,
                OrgMember.status == MemberStatus.ACTIVE,
                User.status == UserStatus.ACTIVE,
            )
        )
        return [
            {"id": row.id, "display_name": row.display_name, "last_login_at": row.last_login_at}
            for row in result.all()
        ]

    raise ValueError(f"Unknown target entity type: {spec.target_entity_type}")
