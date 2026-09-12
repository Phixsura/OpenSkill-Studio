"""R439: skill/project duplication — provenance preservation (R135 anti-
laundering), archived-guard, exercise/deliverable copy, DRAFT reset.

Documented EQUIVALENT mutants (adjudicated): L54/L120 404->405 HTTP
status-class swaps and L59/L124 the 200-char _copy_name truncation bound
(200->201) — a ±1 length on an already-bounded name column.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.skill import ContentStatus
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _setup(db):
    from app.services.organization import OrgService
    from app.services.skill import SkillService

    owner = User(email=f"r439-{uuid.uuid4().hex[:10]}@t.com",
                 password_hash=hash_password("Test123!"), display_name="R439",
                 role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(owner)
    await db.flush()
    org = await OrgService(db).create(name=f"R439 {uuid.uuid4().hex[:5]}",
                                      slug=f"r439-{uuid.uuid4().hex[:10]}",
                                      description=None, created_by=owner.id)
    await db.flush()
    cat = await SkillService(db).create_category(org.id, "AI", None, None, None, owner.id)
    return org, owner, cat


async def test_duplicate_skill_r439(db):
    from app.models.skill import Exercise
    from app.services.duplicate import DuplicateService
    from app.services.skill import SkillService

    org, owner, cat = await _setup(db)
    other_org, _, _ = await _setup(db)
    sksvc = SkillService(db)
    dup = DuplicateService(db)

    skill = await sksvc.create_skill(org.id, cat.id, "Prompting", None, "desc", "# content",
                                     "beginner", 30, ["ai", "nlp"], None, owner.id)
    # licensed-in provenance markers must survive the copy (R135)
    skill.origin_pack_id = "pack-123"
    skill.origin_release_id = "rel-456"
    skill.origin_component_id = "comp-789"
    await sksvc.publish_skill(skill.id)
    # two exercises: one live, one archived (archived must NOT be copied)
    e_live = await sksvc.create_exercise(org.id, skill.id, "Live", "d", "text_answer", {}, 100,
                                         owner.id)
    e_arch = await sksvc.create_exercise(org.id, skill.id, "Arch", "d", "text_answer", {}, 100,
                                         owner.id)
    e_arch.status = ContentStatus.ARCHIVED
    await db.flush()

    # cross-org / archived / missing → SKILL_NOT_FOUND
    with pytest.raises(AppError) as e_x:
        await dup.duplicate_skill(other_org.id, skill.id, owner.id)
    assert e_x.value.code == "SKILL_NOT_FOUND"

    copy = await dup.duplicate_skill(org.id, skill.id, owner.id)
    assert copy.id != skill.id
    assert copy.status == ContentStatus.DRAFT       # reset to draft
    assert copy.name == "Prompting (Copy)"
    assert copy.slug != skill.slug
    assert copy.tags == ["ai", "nlp"]
    # provenance preserved (anti-laundering)
    assert copy.origin_pack_id == "pack-123"
    assert copy.origin_release_id == "rel-456"
    assert copy.origin_component_id == "comp-789"

    # exactly the LIVE exercise is copied (archived skipped), reset to DRAFT
    from sqlalchemy import select

    copied_ex = (await db.execute(
        select(Exercise).where(Exercise.skill_id == copy.id))).scalars().all()
    assert [e.title for e in copied_ex] == ["Live"]
    assert copied_ex[0].status == ContentStatus.DRAFT
    assert copied_ex[0].max_score == 100

    # an ARCHIVED source skill cannot be duplicated
    skill.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError) as e_arch2:
        await dup.duplicate_skill(org.id, skill.id, owner.id)
    assert e_arch2.value.code == "SKILL_NOT_FOUND"


async def test_duplicate_project_r439(db):
    from datetime import UTC, datetime

    from app.models.project import ProjectDeliverable
    from app.services.duplicate import DuplicateService
    from app.services.project import ProjectService

    org, owner, cat = await _setup(db)
    other_org, _, _ = await _setup(db)
    psvc = ProjectService(db)
    dup = DuplicateService(db)

    proj = await psvc.create_project(
        org.id, "Chatbot", None, "desc", "instr", "intermediate", 80,
        [{"criterion": "Q", "max_score": 80}], datetime.now(UTC), None, 25, 3, None, owner.id)
    await psvc.create_deliverable(proj.id, "Report", "d", "text", True, {}, 0)
    await psvc.create_deliverable(proj.id, "Video", None, "file", False, {}, 1)

    # cross-org → PROJECT_NOT_FOUND
    with pytest.raises(AppError) as e_x:
        await dup.duplicate_project(other_org.id, proj.id, owner.id)
    assert e_x.value.code == "PROJECT_NOT_FOUND"

    copy = await dup.duplicate_project(org.id, proj.id, owner.id)
    assert copy.id != proj.id
    assert copy.status == ContentStatus.DRAFT
    assert copy.title == "Chatbot (Copy)"
    assert copy.max_score == 80
    assert copy.max_submissions == 3
    # deadline is intentionally NOT copied
    assert copy.deadline is None
    assert copy.late_penalty_pct == proj.late_penalty_pct

    # all deliverables copied in order
    from sqlalchemy import select

    dels = (await db.execute(
        select(ProjectDeliverable).where(ProjectDeliverable.project_id == copy.id)
        .order_by(ProjectDeliverable.sort_order))).scalars().all()
    assert [d.name for d in dels] == ["Report", "Video"]
    assert dels[0].required is True and dels[1].required is False

    # archived project cannot be duplicated
    proj.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError):
        await dup.duplicate_project(org.id, proj.id, owner.id)
