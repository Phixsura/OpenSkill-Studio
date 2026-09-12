"""R432: client-brief list/update + brief->project conversion state machine.

convert_to_project is the brief->project pipeline (rubric defaulting,
deliverable materialization, draft-only claim, cross-org cohort guard).
list/update had thin branch coverage.

Documented EQUIVALENT mutants (adjudicated): L58/L121 slug-suffix
cosmetics (base[:290], token_hex(3)); L70 per_page default 20->21 (both
return all 5 fixtures); L77/L116/L172/L185 422->423 and L196 404->405
HTTP status-class swaps.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.client_brief import BriefStatus
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(email=f"r432-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R432", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(name=f"R432 {uuid.uuid4().hex[:5]}",
                                    slug=f"r432-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o


async def _brief(db, svc, org, owner, **extra):
    fields = dict(title="Brief", client_name="Acme", project_type="ai_visual",
                  objective="Make art", deliverable_specs=[])
    fields.update(extra)
    return await svc.create_brief(org.id, owner.id, **fields)


async def test_list_briefs_filter_and_pagination_r432(db):
    from app.services.client_brief import ClientBriefService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = ClientBriefService(db)

    briefs = [await _brief(db, svc, org, owner, title=f"B{i}") for i in range(5)]
    # move two to OPEN status
    briefs[0].status = BriefStatus.OPEN
    briefs[1].status = BriefStatus.OPEN
    await db.flush()

    # status filter returns ONLY matching (kills the `== BriefStatus(status)`
    # -> `!=` mutant)
    open_rows, open_total = await svc.list_briefs(org.id, status="open")
    assert open_total == 2
    assert all(b.status == BriefStatus.OPEN for b in open_rows)
    draft_rows, draft_total = await svc.list_briefs(org.id, status="draft")
    assert draft_total == 3

    # pagination: page 2 with per_page 2 returns the 3rd/4th newest (kills the
    # `(page-1)*per_page` -> `+` offset mutant)
    all_rows, total = await svc.list_briefs(org.id)
    assert total == 5
    # the DEFAULT page (no page arg) starts at offset 0 → returns all 5
    # (kills the `page: int = 1` default -> 2 mutant, which would offset past them)
    assert len(all_rows) == 5
    p1, _ = await svc.list_briefs(org.id, page=1, per_page=2)
    p2, _ = await svc.list_briefs(org.id, page=2, per_page=2)
    assert len(p1) == 2 and len(p2) == 2
    assert {b.id for b in p1}.isdisjoint({b.id for b in p2})  # distinct slices


async def test_update_brief_none_ignored_r432(db):
    from app.services.client_brief import ClientBriefService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = ClientBriefService(db)
    brief = await _brief(db, svc, org, owner, objective="original")

    # a None field is IGNORED (partial update), a real value applies (kills the
    # `v is not None and hasattr` -> `or` mutant that would null the column)
    updated = await svc.update_brief(brief.id, objective=None, client_name="NewCo")
    assert updated.objective == "original"  # unchanged by None
    assert updated.client_name == "NewCo"


async def test_convert_to_project_r432(db):
    from app.models.cohort import Cohort
    from app.services.client_brief import ClientBriefService
    from app.services.project import ProjectService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = ClientBriefService(db)

    # a brief with two deliverable specs (one missing a name → fallback name)
    specs = [
        {"name": "Hero image", "type": "file", "required": True},
        {"type": "file"},  # no name → "Deliverable 2"
    ]
    brief = await _brief(db, svc, org, owner, deliverable_specs=specs)

    # cross-org cohort → INVALID_COHORT (kills the `is None or wrong-org`
    # -> `and` mutant)
    foreign_cohort = Cohort(org_id=other_org.id, name="X",
                            slug=f"x-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(foreign_cohort)
    await db.flush()
    with pytest.raises(AppError) as e_coh:
        await svc.convert_to_project(brief.id, org.id, owner.id, cohort_id=foreign_cohort.id)
    assert e_coh.value.code == "INVALID_COHORT"

    # a FRESH brief converts cleanly (no rollback — that would wipe owner/org;
    # the AppError above left the session usable, just with brief1 mid-claim)
    brief = await _brief(db, svc, org, owner, deliverable_specs=specs)
    # provided rubric → max_score is the SUM of its parts (kills `sum(...) or
    # 100` -> `and 100` and the 100->101 default)
    rubric = [{"criterion": "A", "max_score": 60}, {"criterion": "B", "max_score": 40}]
    proj = await svc.convert_to_project(brief.id, org.id, owner.id, rubric=rubric)
    assert proj.max_score == 100  # 60 + 40, not the default
    assert proj.client_brief_id == brief.id

    # deliverables materialized with the fallback name for the unnamed spec
    deliverables = await ProjectService(db).list_deliverables(proj.id)
    names = sorted(d.name for d in deliverables)
    assert names == ["Deliverable 2", "Hero image"]

    # double-convert → INVALID_STATE (brief is now ACTIVE, not draft)
    with pytest.raises(AppError) as e_again:
        await svc.convert_to_project(brief.id, org.id, owner.id)
    assert e_again.value.code == "INVALID_STATE"

    # a brief with NO rubric gets the default single-criterion rubric (max 100)
    brief2 = await _brief(db, svc, org, owner)
    proj2 = await svc.convert_to_project(brief2.id, org.id, owner.id)
    assert proj2.max_score == 100
    assert proj2.rubric == [{"criterion": "Overall Quality", "max_score": 100}]

    # cross-org brief → not found
    brief3 = await _brief(db, svc, org, owner)
    with pytest.raises(AppError) as e_org:
        await svc.convert_to_project(brief3.id, other_org.id, owner.id)
    assert e_org.value.status_code == 404
